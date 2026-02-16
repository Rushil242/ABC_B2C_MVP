
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, auth_utils
from ..services import itr_service
from pydantic import BaseModel
import subprocess
import os
import glob
import json
import logging
import sys
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
DOWNLOAD_DIR = os.path.join(AUTOMATION_DIR, "downloads", "filedreturns")

class SyncRequest(BaseModel):
    password: str

def bg_sync_workflow(user_pan: str, password: str):
    """
    Runs the scraper and ingests data.
    """
    logging.info(f"Starting Sync Workflow for {user_pan}")
    
    # 1. Run Scraper
    try:
        # Prepare Environment Variables
        env = os.environ.copy()
        env["INCOME_TAX_USERNAME"] = user_pan
        env["INCOME_TAX_PASSWORD"] = password
        
        # run_workflow.py filed_returns --headless
        result = subprocess.run(
            [sys.executable, "run_workflow.py", "filed_returns", "--headless"],
            cwd=AUTOMATION_DIR,
            capture_output=True,
            text=True,
            env=env
        )
        logging.info(f"Scraper Output: {result.stdout}")
        if result.returncode != 0:
            logging.error(f"Scraper Failed: {result.stderr}")
            return
            
    except Exception as e:
        logging.error(f"Failed to launch scraper: {e}")
        return

    # 2. Ingest Data
    # ... (Rest remains same)
    logging.info("Scraping complete. Ingesting data...")
    
    # Create new DB Session
    db = database.SessionLocal()
    try:
        json_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.json"))
        count = 0
        for json_file in json_files:
            if "results.json" in json_file: continue # Skip metadata file if any
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                success, msg = itr_service.process_itr_data(db, user_pan, data)
                if success:
                    count += 1
                    logging.info(f"Ingested {os.path.basename(json_file)}")
                else:
                    logging.warning(f"Failed to ingest {json_file}: {msg}")
                    
            except Exception as e:
                logging.error(f"Error reading {json_file}: {e}")
        
        logging.info(f"Sync Complete. Ingested {count} files.")
        
    except Exception as e:
        logging.error(f"Ingestion Error: {e}")
    finally:
        db.close()

@router.post("/itr")
def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """
    Triggers the background scraping workflow.
    """
    background_tasks.add_task(bg_sync_workflow, current_user.pan, request.password)
    return {"status": "started", "message": "Sync started in background. Dashboard will update shortly."}
