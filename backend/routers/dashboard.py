
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth_utils
from typing import List

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

@router.get("", response_model=schemas.DashboardResponse)
def get_dashboard_data(current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(database.get_db)):
    # Fetch related data using relationships
    itr = db.query(models.ITR_Filing).filter(models.ITR_Filing.user_pan == current_user.pan).order_by(models.ITR_Filing.ay.desc()).first()
    risks = db.query(models.Risk).filter(models.Risk.user_pan == current_user.pan).all()
    opportunities = db.query(models.Opportunity).filter(models.Opportunity.user_pan == current_user.pan).all()
    
    # New tables
    advance_tax = db.query(models.AdvanceTax).filter(models.AdvanceTax.user_pan == current_user.pan).all()
    tds_entries = db.query(models.TDS_Entry).filter(models.TDS_Entry.user_pan == current_user.pan).all()

    # Map TDS_Entry to TDSSchema (if needed, but field names match mostly)
    # The schema expects 'tds_tcs' list, so we pass tds_entries there.
    
    return {
        "user": current_user,
        "itr": itr,
        "risks": risks,
        "opportunities": opportunities,
        "advance_tax": advance_tax,
        "tds_tcs": tds_entries
    }
