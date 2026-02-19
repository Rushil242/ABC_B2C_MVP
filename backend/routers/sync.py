
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from sqlalchemy.orm import Session
from .. import database, models, auth_utils
from ..services import itr_service, sync_service
from pydantic import BaseModel
import subprocess
import os
import glob
import json
import logging
import sys
import time

router = APIRouter(
    prefix="/api/sync",
    tags=["Automation"]
)

# Determine PROJECT_ROOT dynamically to work on any machine
# sync.py is in backend/routers/ -> go up 2 levels
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
AUTOMATION_DIR = os.path.join(PROJECT_ROOT, "automation")
DOWNLOAD_DIR_BASE = os.path.join(AUTOMATION_DIR, "downloads")

# In-memory state for sync status: { "PAN123": { "status": "running", "step": "ITR", "details": "..." } }
SYNC_STATE = {}

class SyncRequest(BaseModel):
    password: str

def update_sync_state(pan, step, status_msg, state="running"):
    SYNC_STATE[pan] = {
        "status": state, # running, completed, failed
        "step": step,
        "message": status_msg,
        "timestamp": time.time()
    }

def run_automation_workflow(workflow_name: str, user_pan: str, password: str, db: Session):
    """
    Generic function to run an automation workflow and ingest results.
    """
    logging.info(f"Starting {workflow_name} Workflow for {user_pan}")
    
    # 1. Run Scraper
    try:
        env = os.environ.copy()
        env["INCOME_TAX_USERNAME"] = user_pan
        env["INCOME_TAX_PASSWORD"] = password
        
        # run_workflow.py <workflow_name> --headless
        result = subprocess.run(
            [sys.executable, "run_workflow.py", workflow_name, "--headless"],
            cwd=AUTOMATION_DIR,
            capture_output=True,
            text=True,
            env=env
        )
        
        # Check stdout for [DATA] JSON to catch specific application errors even if return code is 0 (or not)
        output_lines = result.stdout.splitlines()
        error_info = None
        for line in output_lines:
            if line.startswith("[DATA]"):
                try:
                    data = json.loads(line[7:])
                    if data.get("status") == "error":
                        error_info = data
                except:
                    pass

        if result.returncode != 0 or error_info:
            error_msg = result.stderr
            if error_info:
                error_msg = error_info.get("message", "Unknown error")
                if error_info.get("code") == "INVALID_CREDENTIALS" or "Invalid User ID or Password" in error_msg:
                     error_msg = "Invalid Password. Please check your credentials."
            
            logging.error(f"Workflow Failed: {error_msg}")
            # If verify credentials failed, we should know
            return False, error_msg

        logging.info(f"Workflow Output: {result.stdout}")
            
    except Exception as e:
        logging.error(f"Failed to launch workflow {workflow_name}: {e}")
        return False, str(e)

    # 2. Ingest Data based on workflow type
    logging.info(f"{workflow_name} scraping complete. Ingesting artifacts...")
    
    # The python scripts generate directories based on class name.
    # BaseWorkflow: self.__class__.__name__.replace('Workflow', '').lower()
    # verify_credentials -> VerifyCredentialsWorkflow -> verifycredentials
    # filed_returns -> FiledReturnsWorkflow -> filedreturns
    # ais_download -> AISDownloadWorkflow -> aisdownload
    # form_26as -> Form26ASWorkflow -> form26as
    # So we strictly remove underscores from the passed snake_case workflow_name
    folder_name = workflow_name.replace("_", "")
    
    workflow_download_dir = os.path.join(DOWNLOAD_DIR_BASE, folder_name)
    results_file = os.path.join(workflow_download_dir, "results.json")
    
    if not os.path.exists(results_file):
        logging.warning(f"No results.json found for {workflow_name} at {results_file}")
        # Only return False if it was expected to produce results. Verify might not if it just checks login.
        if workflow_name == "verify_credentials":
             return True, "Success"
        return False, "No results generated"

    try:
        with open(results_file, 'r') as f:
            results_data = json.load(f)
        
        # Dispatch to appropriate service
        if workflow_name == "filed_returns":
             # Existing logic for ITR
             count = 0
             for item in results_data:
                 if "file" in item and item["file"].endswith(".json"):
                     try:
                         with open(item["file"], 'r') as jf:
                             data = json.load(jf)
                         success, msg = itr_service.process_itr_data(db, user_pan, data)
                         if success: count += 1
                     except Exception as e:
                         logging.error(f"Failed to process ITR file {item.get('file')}: {e}")
             logging.info(f"Ingested {count} ITR files.")

        elif workflow_name == "ais_download":
            # AIS Download workflow saves file paths in results.json
            count = 0
            for item in results_data:
                file_path = item.get("file")
                if file_path and os.path.exists(file_path):
                     try:
                         # AIS download usually gives a JSON file if we selected JSON button
                         # We try to read it
                         with open(file_path, 'r') as af:
                             ais_content = json.load(af)
                         success, msg = sync_service.process_ais_data(db, user_pan, ais_content)
                         if success: count += 1
                     except json.JSONDecodeError:
                         logging.error(f"Failed to parse AIS JSON {file_path}")
                     except Exception as e:
                         logging.error(f"Failed to process AIS file {file_path}: {e}")
            logging.info(f"Ingested {count} AIS files.")

        elif workflow_name == "form_26as":
            for item in results_data:
                if "file" in item:
                    sync_service.process_26as_file(db, user_pan, item["file"])

        elif workflow_name == "eproceedings":
            for item in results_data:
                if "file" in item:
                    sync_service.process_eproceedings_file(db, user_pan, item["file"])
        
        elif workflow_name == "verify_credentials":
            logging.info("Credentials verification successful.")
            
        return True, "Success"

    except Exception as e:
        logging.error(f"Error reading results.json or ingestion: {e}")
        return False, str(e)

def bg_sync_wrapper(workflow_name: str, user_pan: str, password: str):
    """
    Wrapper to get a new DB session for the background task.
    """
    db = database.SessionLocal()
    try:
        run_automation_workflow(workflow_name, user_pan, password, db)
    finally:
        db.close()

def bg_sync_all(user_pan: str, password: str):
    """
    Runs all sync workflows sequentially with status updates.
    """
    db = database.SessionLocal()
    try:
        # 1. Verify Credentials
        update_sync_state(user_pan, "Verify", "Verifying credentials...")
        success, msg = run_automation_workflow("verify_credentials", user_pan, password, db)
        if not success:
             update_sync_state(user_pan, "Verify", msg, "failed")
             return
        
        # 2. ITR
        update_sync_state(user_pan, "ITR", "Fetching Income Tax Returns...")
        run_automation_workflow("filed_returns", user_pan, password, db)
        
        # 3. AIS
        update_sync_state(user_pan, "AIS", "Downloading AIS/TIS data...")
        run_automation_workflow("ais_download", user_pan, password, db)
        
        # 4. Form 26AS
        update_sync_state(user_pan, "26AS", "Downloading Form 26AS...")
        run_automation_workflow("form_26as", user_pan, password, db)
        
        # 5. Notices
        update_sync_state(user_pan, "Notices", "Checking for Notices...")
        run_automation_workflow("eproceedings", user_pan, password, db)
        
        update_sync_state(user_pan, "Complete", "All syncs completed successfully.", "completed")
        logging.info("All sync workflows completed.")
        
    except Exception as e:
        logging.error(f"Error in bg_sync_all: {e}")
        update_sync_state(user_pan, "Error", f"Sync failed: {str(e)}", "failed")
    finally:
        db.close()

# Endpoints

@router.get("/status")
def get_sync_status(current_user: models.User = Depends(auth_utils.get_current_user)):
    return SYNC_STATE.get(current_user.pan, {"status": "idle", "message": "No active sync."})

@router.post("/all")
def trigger_all_sync(request: SyncRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth_utils.get_current_user)):
    background_tasks.add_task(bg_sync_all, current_user.pan, request.password)
    return {"status": "started", "message": "Full profile sync started. This may take a few minutes."}

@router.post("/itr")
def trigger_itr_sync(request: SyncRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth_utils.get_current_user)):
    background_tasks.add_task(bg_sync_wrapper, "filed_returns", current_user.pan, request.password)
    return {"status": "started", "message": "ITR Sync started in background."}

@router.post("/ais")
def trigger_ais_sync(request: SyncRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth_utils.get_current_user)):
    background_tasks.add_task(bg_sync_wrapper, "ais_download", current_user.pan, request.password)
    return {"status": "started", "message": "AIS Sync started in background."}

@router.post("/26as")
def trigger_26as_sync(request: SyncRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth_utils.get_current_user)):
    background_tasks.add_task(bg_sync_wrapper, "form_26as", current_user.pan, request.password)
    return {"status": "started", "message": "Form 26AS Sync started in background."}

@router.post("/eproceedings")
def trigger_notices_sync(request: SyncRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth_utils.get_current_user)):
    background_tasks.add_task(bg_sync_wrapper, "eproceedings", current_user.pan, request.password)
    return {"status": "started", "message": "E-Proceedings Sync started in background."}

@router.post("/verify")
def trigger_verify(request: SyncRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth_utils.get_current_user)):
    background_tasks.add_task(bg_sync_wrapper, "verify_credentials", current_user.pan, request.password)
    return {"status": "started", "message": "Credential verification started."}
