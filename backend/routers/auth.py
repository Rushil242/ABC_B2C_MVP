
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Form
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth_utils
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), questionnaire_data: str = Form(None), db: Session = Depends(database.get_db)):
    # 1. DEMO MODE CHECK
    if form_data.username == "ABCDE1234F" and form_data.password == "demo123":
        # Ensure Demo User Exists in DB with Frontend required fields
        user = db.query(models.User).filter(models.User.pan == "ABCDE1234F").first()
        if not user:
            user = models.User(
                pan="ABCDE1234F", 
                name="Rajesh Kumar Sharma", # Matches Frontend Mock
                password_hash=auth_utils.get_password_hash("demo123"),
                email="demo@abc.com",
                dob="15-08-1985" # Matches Frontend Mock
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Populate Mock Data for Dashboard if empty
        if not user.risks:
            # Add Mock Risks
            db.add(models.Risk(user_pan=user.pan, ay="2023-24", title="Mismatch in TDS claimed vs Form 26AS", severity="High", description="TDS amount claimed ₹12,000 more than reflected in 26AS", solutions='["Verify Form 26AS", "File rectification"]', amount_involved=12000))
            db.add(models.Risk(user_pan=user.pan, ay="2022-23", title="Interest income not declared", severity="Med", description="FD interest of ₹45,000 from SBI not reported", solutions='["File revised return"]', amount_involved=45000))
            
            # Add Mock Opportunities
            db.add(models.Opportunity(user_pan=user.pan, ay="2023-24", title="Section 80C – PPF contribution not claimed", description="Missed deduction", potential_savings=46800))
            
            # Add Mock Advance Tax
            db.add(models.AdvanceTax(user_pan=user.pan, quarter="Q1", section="234C", due_date="15-Jun-2025", amount="₹25,000", status="Paid", reminder="—"))
            
            # Add Mock TDS
            db.add(models.TDS_Entry(user_pan=user.pan, type="TDS", section="192", date="31-Mar-2025", tds_amount="₹1,20,000", total_amount="₹12,00,000"))
            
            # Add Mock ITR Filing (For Profile Page)
            # We construct a minimal JSON that matches the structure expected by profile.py
            import json
            mock_itr_json = {
                "ITR": {
                    "ITR2": {
                        "Form_ITR2": {
                            "AssessmentYear": "2025",
                        },
                        "PartA_GEN1": {
                            "PersonalInfo": {
                                "AssesseeName": {
                                    "FirstName": "Rajesh",
                                    "SurNameOrOrgName": "Kumar Sharma"
                                },
                                "Address": {
                                    "ResidenceNo": "42",
                                    "ResidenceName": "Sector 18",
                                    "RoadOrStreet": "Dwarka",
                                    "LocalityOrArea": "New Delhi",
                                    "CityOrTownOrDistrict": "New Delhi",
                                    "StateCode": "11",
                                    "PinCode": 110078,
                                    "CountryCodeMobile": 91,
                                    "MobileNo": 9876543210
                                }
                            },
                             "FilingStatus": {
                                "ReceiptNo": "DEMO_RECEIPT_001",
                                "OrigRetFiledDate": "2025-07-31"
                            }
                        },
                        "PartB-TI": {
                            "TotalIncome": 1500000
                        },
                        "PartB_TTI": {
                            "NetTaxLiability": 150000
                        }
                    }
                }
            }
            
            db.add(models.ITR_Filing(
                user_pan=user.pan,
                ack_num="DEMO_RECEIPT_001",
                ay="2025-26",
                filing_date="2025-07-31",
                total_income=1500000,
                tax_payable=150000,
                itr_type="ITR-2",
                status="Filed",
                refund_amount="0",
                raw_data=json.dumps(mock_itr_json)
            ))
            
            # Seed Past ITRs
            db.add(models.ITR_Filing(
                user_pan=user.pan, ack_num="DEMO_REC_24", ay="2024-25", filing_date="2024-07-31", 
                total_income=1400000, tax_payable=120000, itr_type="ITR-1", status="Processed", refund_amount="₹12,400", raw_data="{}"
            ))
            db.add(models.ITR_Filing(
                user_pan=user.pan, ack_num="DEMO_REC_23", ay="2023-24", filing_date="2023-07-31", 
                total_income=1300000, tax_payable=100000, itr_type="ITR-1", status="Processed", refund_amount="0", raw_data="{}"
            ))

            # Seed Notices
            db.add(models.Notice(
                user_pan=user.pan, category="Intimation", section="143(1)", date="2024-12-15",
                description="Intimation under section 143(1) for AY 2024-25", status="Pending"
            ))
            db.add(models.Notice(
                user_pan=user.pan, category="Defective Notice", section="139(9)", date="2023-09-10",
                description="Defective return notice for AY 2023-24", status="Resolved"
            ))
            
            db.commit()

        access_token = auth_utils.create_access_token(data={"sub": user.pan})
        return {"access_token": access_token, "token_type": "bearer"}

    # 2. LOCAL AUTH ONLY (Login)
    user = db.query(models.User).filter(models.User.pan == form_data.username.upper()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not registered. Please register first.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth_utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. TRIGGER RULE ENGINE (Refresh Risks/Opportunities on Login)
    from ..services import itr_service
    # Run in background to not block login? Or synchronously? 
    # Synchronously is better for immediate dashboard update if fast (<1s).
    itr_service.run_rules_for_user(db, user.pan)
    
    # Update Questionnaire Data if provided
    if questionnaire_data:
         user.questionnaire_data = questionnaire_data
         db.commit()

    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.pan}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.Token)
def register(background_tasks: BackgroundTasks, user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Check if user already exists
    db_user = db.query(models.User).filter(models.User.pan == user.pan).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="User with this PAN already exists"
        )
    
    # 2. VERIFY ITR CREDENTIALS (Using Automation)
    import subprocess
    import os
    import json
    
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.dirname(CURRENT_DIR)
    PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
    AUTOMATION_DIR = os.path.join(PROJECT_ROOT, "automation")
    
    env = os.environ.copy()
    env["INCOME_TAX_USERNAME"] = user.pan.upper()
    env["INCOME_TAX_PASSWORD"] = user.password

    print(f"Verifying ITR credentials for {user.pan}...")
    try:
        # Run verify_credentials workflow
        result = subprocess.run(
            ["python", "run_workflow.py", "verify_credentials", "--headless"],
            cwd=AUTOMATION_DIR,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode != 0:
            print(f"VERIFICATION FAILED: {result.stderr}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ITR Verification Failed: Invalid PAN or Password.",
            )
        
        # Parse stdout for [DATA] JSON
        scraped_name = None
        for line in result.stdout.splitlines():
            if line.startswith("[DATA]"):
                try:
                    data = json.loads(line.replace("[DATA]", "").strip())
                    if data.get("status") == "success":
                        scraped_name = data.get("name")
                except json.JSONDecodeError:
                    pass
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"AUTH ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed due to internal error",
        )

    try:
        # 3. Create new user with Questionnaire Data
        hashed_password = auth_utils.get_password_hash(user.password)
        
        # Use scraped name if provided name is null (which it is from frontend)
        final_name = user.name
        if not final_name and scraped_name:
            final_name = scraped_name
            
        # Serialize questionnaire data if present
        q_data_str = None
        if user.questionnaire_data:
            q_data_str = json.dumps(user.questionnaire_data)
            
        new_user = models.User(
            pan=user.pan,
            name=final_name,
            email=user.email,
            dob=user.dob,
            password_hash=hashed_password,
            questionnaire_data=q_data_str
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 4. Trigger Sync
        from .sync import bg_sync_workflow
        background_tasks.add_task(bg_sync_workflow, new_user.pan, user.password)
        
        # 5. Auto-login (Create Token)
        access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_utils.create_access_token(
            data={"sub": new_user.pan}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"REGISTER ERROR: {str(e)}") # Print to console
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
