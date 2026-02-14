
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database, rule_engine
import json

router = APIRouter(
    prefix="/api/data",
    tags=["Data Ingestion"]
)

# Pydantic model for incoming data (flexible for now)
from pydantic import BaseModel, Json
class ScrapedData(BaseModel):
    pan: str
    itr_data: Json 
    ais_data: list # List of dicts

@router.post("/upload")
def upload_scraped_data(data: ScrapedData, db: Session = Depends(database.get_db)):
    # 1. Find or Create User
    user = db.query(models.User).filter(models.User.pan == data.pan).first()
    if not user:
        # Create user (Password would be set later or via email flow in real app)
        user = models.User(pan=data.pan, name="Scraped User", password_hash="TEMP_HASH") 
        db.add(user)
        db.commit()
    
    # 2. Process ITR Data via Service
    from ..services import itr_service
    
    # Check if itr_data is string or dict
    itr_json = data.itr_data
    if isinstance(itr_json, str):
        itr_json = json.loads(itr_json)
        
    success, message = itr_service.process_itr_data(db, data.pan, itr_json)
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Error processing data: {message}")

    return {"status": "success", "message": "Data ingested and analyzed successfully"}
