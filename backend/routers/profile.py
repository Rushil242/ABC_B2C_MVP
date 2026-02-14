
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth_utils
import json
import logging

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"]
)

@router.get("", response_model=schemas.UserProfile)
def get_user_profile(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Fetch Latest ITR
    # itr = db.query(models.ITR_Filing).filter(models.ITR_Filing.user_pan == current_user.pan).order_by(models.ITR_Filing.ay.desc()).first()
    itr = db.query(models.ITR_Filing).filter(models.ITR_Filing.user_pan == current_user.pan).first()
    
    address = "N/A"
    phone = "N/A"
    
    if not itr:
        address = "DEBUG: ITR RECORD NOT FOUND IN DB"
    elif not itr.raw_data:
        address = "DEBUG: ITR FOUND BUT RAW_DATA IS EMPTY"
    
    ao_details = {
        "aoCode": "N/A", "aoType": "N/A", "range": "N/A", 
        "circle": "N/A", "ward": "N/A", "city": "N/A"
    }

    if itr and itr.raw_data:
        try:
            itr_json = json.loads(itr.raw_data)
            # Safe extraction logic
            itr2_form = itr_json.get("ITR", {}).get("ITR2", {})
            personal_info = itr2_form.get("PartA_GEN1", {}).get("PersonalInfo", {})
            
            # Address
            addr_obj = personal_info.get("Address", {})
            parts = [
                addr_obj.get("ResidenceNo"),
                addr_obj.get("ResidenceName"),
                addr_obj.get("RoadOrStreet"),
                addr_obj.get("LocalityOrArea"),
                addr_obj.get("CityOrTownOrDistrict"),
                f"{addr_obj.get('StateCode')}-{addr_obj.get('PinCode')}"
            ]
            address = ", ".join([str(p) for p in parts if p])
            
            # Phone
            phone = f"+{addr_obj.get('CountryCodeMobile', '91')} {addr_obj.get('MobileNo', '')}"

        except Exception as e:
            logging.warning(f"PROFILE PARSE ERROR: {e}")
            if 'itr_json' in locals():
                logging.warning(f"ITR JSON TYPE: {type(itr_json)}")
                logging.warning(f"ITR JSON VAL: {str(itr_json)[:100]}")
            address = f"ERROR: {str(e)}"

    return {
        "personal_info": current_user,
        "address": address,
        "phone": phone,
        "ao_details": ao_details
    }
