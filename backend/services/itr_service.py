
from sqlalchemy.orm import Session
from .. import models, rule_engine
import json
import logging

def process_itr_data(db: Session, pan: str, itr_json: dict):
    """
    Processes a single ITR JSON:
    1. Extracts key fields (AY, Income, Tax).
    2. Upserts ITR_Filing record.
    3. Runs Rule Engine to generate Risks/Opportunities.
    """
    try:
        # 1. Extract Fields (Robust)
        # Note: Structure varies by ITR type (ITR-1, ITR-2). 
        # This logic is primarily for ITR-2 based on sample, but we add safety checks.
        
        # Try finding Form_ITR2 or Form_ITR1
        itr_root = itr_json.get("ITR", {})
        form_type = next(iter(itr_root)) if itr_root else "Unknown" # e.g. ITR2
        form_data = itr_root.get(form_type, {})
        
        # Generic Paths (Attempt to standardize)
        # Most have CreationInfo, Form_ITR*, PartA_GEN1, PartB-TI, PartB_TTI
        
        # AY
        ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
        
        # Personal Info
        personal_info = form_data.get("PartA_GEN1", {}).get("PersonalInfo", {})
        
        # Filing Status
        filing_status = form_data.get("PartA_GEN1", {}).get("FilingStatus", {})
        ack_num = filing_status.get("ReceiptNo", "UNKNOWN_ACK")
        filing_date = filing_status.get("OrigRetFiledDate", "Unknown")
        
        # Income & Tax
        part_b_ti = form_data.get("PartB-TI", {})
        total_income = part_b_ti.get("TotalIncome", 0)
        
        part_b_tti = form_data.get("PartB_TTI", {})
        tax_payable = part_b_tti.get("NetTaxLiability", 0)
        refund = part_b_tti.get("Refund", {}).get("RefundDue", "0") # Check path for Refund

        # Upsert User Name if available
        user = db.query(models.User).filter(models.User.pan == pan).first()
        if user and personal_info:
             if not user.name or user.name == "Scraped User":
                first = personal_info.get("AssesseeName", {}).get("FirstName", "")
                last = personal_info.get("AssesseeName", {}).get("SurNameOrOrgName", "")
                user.name = f"{first} {last}".strip()
                db.add(user)

        # Upsert ITR Filing
        existing_itr = db.query(models.ITR_Filing).filter(models.ITR_Filing.ack_num == ack_num).first()
        
        if existing_itr:
            existing_itr.ay = ay
            existing_itr.filing_date = filing_date
            existing_itr.total_income = total_income
            existing_itr.tax_payable = tax_payable
            existing_itr.itr_type = form_type
            existing_itr.refund_amount = str(refund)
            existing_itr.raw_data = json.dumps(itr_json)
            # status? We assume processed/filed if we have the JSON
        else:
            new_itr = models.ITR_Filing(
                user_pan=pan,
                ack_num=ack_num,
                ay=ay,
                filing_date=filing_date,
                total_income=total_income,
                tax_payable=tax_payable,
                itr_type=form_type,
                status="Filed", # Default
                refund_amount=str(refund),
                raw_data=json.dumps(itr_json)
            )
            db.add(new_itr)
        
        # Run Rule Engine
        # Clear old risks/opps for this AY/PAN? For now, we append.
        # Ideally we should deduplicate.
        
        risks = rule_engine.evaluate_risks(itr_json)
        for risk in risks:
            # Simple dedup check based on title/code?
            # For now, just add.
            db.add(models.Risk(user_pan=pan, **risk))
            
        opps = rule_engine.evaluate_opportunities(itr_json)
        for opp in opps:
            db.add(models.Opportunity(user_pan=pan, **opp))

        db.commit()
        return True, "Processed successfully"

    except Exception as e:
        logging.error(f"Error processing ITR: {e}")
        db.rollback()
        return False, str(e)
