
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
    # Fetch Latest ITR by Assessment Year (descending)
    itr = db.query(models.ITR_Filing).filter(
        models.ITR_Filing.user_pan == current_user.pan
    ).order_by(models.ITR_Filing.ay.desc()).first()
    
    address = "None"
    phone = "+91"
    email = current_user.email or "N/A"
    name = current_user.name or "N/A"
    dob = current_user.dob or "N/A"
    
    ao_details = {
        "aoCode": "N/A", "aoType": "N/A", "range": "N/A", 
        "circle": "N/A", "ward": "N/A", "city": "N/A"
    }

    if itr and itr.raw_data:
        try:
            itr_json = json.loads(itr.raw_data)
            itr_root = itr_json.get("ITR", {})
            
            # Detect ITR form type
            form_type = next(iter(itr_root)) if itr_root else "Unknown"
            form_data = itr_root.get(form_type, {})
            
            # Extract personal info based on form type
            if "ITR1" in form_type or "ITR4" in form_type:
                # ITR1/ITR4 Structure: PersonalInfo is directly under form
                personal_info = form_data.get("PersonalInfo", {})
            else:
                # ITR2/ITR3 Structure: PersonalInfo is under PartA_GEN1
                personal_info = form_data.get("PartA_GEN1", {}).get("PersonalInfo", {})
            
            # Extract name
            assessee_name = personal_info.get("AssesseeName", {})
            first_name = assessee_name.get("FirstName", "")
            middle_name = assessee_name.get("MiddleName", "")
            last_name = assessee_name.get("SurNameOrOrgName", "")
            full_name = f"{first_name} {middle_name} {last_name}".strip()
            if full_name:
                name = full_name
                # Update user record if name is missing or generic
                if not current_user.name or current_user.name == "Scraped User":
                    current_user.name = name
                    db.add(current_user)
                    db.commit()
            
            # Extract DOB
            if personal_info.get("DOB"):
                dob = personal_info.get("DOB")
                # Update user record if DOB is missing
                if not current_user.dob:
                    current_user.dob = dob
                    db.add(current_user)
                    db.commit()
            
            # Extract Address
            addr_obj = personal_info.get("Address", {})
            parts = [
                addr_obj.get("ResidenceNo"),
                addr_obj.get("ResidenceName"),
                addr_obj.get("RoadOrStreet"),
                addr_obj.get("LocalityOrArea"),
                addr_obj.get("CityOrTownOrDistrict"),
            ]
            pin_code = addr_obj.get("PinCode")
            if pin_code:
                parts.append(str(pin_code))
            
            address_str = ", ".join([str(p) for p in parts if p])
            if address_str:
                address = address_str
            
            # Extract Phone
            country_code = addr_obj.get("CountryCodeMobile", 91)
            mobile_no = addr_obj.get("MobileNo", "")
            if mobile_no:
                phone = f"+{country_code} {mobile_no}"
            
            # Extract Email
            email_addr = addr_obj.get("EmailAddress", "")
            if email_addr:
                email = email_addr

        except Exception as e:
            logging.error(f"Profile parse error: {e}", exc_info=True)

    return {
        "personal_info": {
            "name": name,
            "pan": current_user.pan,
            "dob": dob,
            "email": email
        },
        "address": address,
        "phone": phone,
        "ao_details": ao_details
    }

class QuestionnaireUpdate(schemas.BaseModel):
    items: dict

@router.put("/questionnaire")
def update_questionnaire(
    data: QuestionnaireUpdate,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    try:
        current_user.questionnaire_data = json.dumps(data.items)
        db.add(current_user)
        db.commit()
        return {"status": "success", "message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

