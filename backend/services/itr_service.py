
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
        # 1. Extract Fields
        itr_root = itr_json.get("ITR", {})
        form_type = next(iter(itr_root)) if itr_root else "Unknown"
        form_data = itr_root.get(form_type, {})
        
        # Defaults
        ay = "Unknown"
        ack_num = "UNKNOWN_ACK"
        filing_date = "Unknown"
        total_income = 0.0
        tax_payable = 0.0
        refund = "0"
        
        # Branch Logic based on Form Type (ITR-1/ITR-4 vs ITR-2/ITR-3)
        if "ITR1" in form_type or "ITR4" in form_type:
             # Structure: ITR1 -> Form_ITR1, PersonalInfo, FilingStatus, ITR1_IncomeDeductions
             ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
             
             personal_info = form_data.get("PersonalInfo", {})
             filing_status = form_data.get("FilingStatus", {})
             ack_num = filing_status.get("ReceiptNo", "UNKNOWN_ACK") # Or ReturnFileSec?
             # Note: ReceiptNo might not be in FilingStatus for ITR-1 sometimes, check metadata?
             # Actually, AcknowledgementNumber is usually in ITR-V, but in ITR JSON?
             # Let's try finding AcknowledgementNumber in 'FilingStatus' or 'PartA_GEN1' equiv.
             # In the sample provided, FilingStatus has ReturnFileSec, Date, but AckNo?
             # AckNo is often missing in raw JSON unless processed.
             # We will use what we can find. Accessing 'AckNum' if present.
             ack_num = filing_status.get("AcknowledgementNumber", filing_status.get("ReceiptNo", "Pending"))
             
             # For ITR1/4: Try DateOfFiling first, then OrigRetFiledDate, then use JSONCreationDate as fallback
             filing_date = filing_status.get("DateOfFiling", filing_status.get("OrigRetFiledDate", "Unknown"))
             if filing_date == "Unknown":
                 # Fallback to JSON creation date if filing date is not available
                 creation_info = form_data.get("CreationInfo", {})
                 filing_date = creation_info.get("JSONCreationDate", "Unknown")
             
             # Income
             inc_ded = form_data.get(f"{form_type}_IncomeDeductions", {})
             total_income = float(inc_ded.get("TotalIncome", 0))
             
             # Tax
             tax_comp = form_data.get(f"{form_type}_TaxComputation", {})
             tax_payable = float(tax_comp.get("NetTaxLiability", 0))
             
             # Refund (ITR1 -> Refund -> RefundDue)
             refund = form_data.get("Refund", {}).get("RefundDue", "0")

        else:
            # Structure: ITR2 -> PartA_GEN1, PartB-TI
            ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
            
            personal_info = form_data.get("PartA_GEN1", {}).get("PersonalInfo", {})
            filing_status = form_data.get("PartA_GEN1", {}).get("FilingStatus", {})
            ack_num = filing_status.get("AcknowledgementNumber", filing_status.get("ReceiptNo", "Pending"))
            # For ITR2/3: Try DateOfFiling first, then OrigRetFiledDate, then JSONCreationDate
            filing_date = filing_status.get("DateOfFiling", filing_status.get("OrigRetFiledDate", "Unknown"))
            if filing_date == "Unknown":
                creation_info = form_data.get("CreationInfo", {})
                filing_date = creation_info.get("JSONCreationDate", "Unknown")
            
            part_b_ti = form_data.get("PartB-TI", {})
            total_income = float(part_b_ti.get("TotalIncome", 0))
            
            part_b_tti = form_data.get("PartB_TTI", {})
            tax_payable = float(part_b_tti.get("NetTaxLiability", 0))
            refund = part_b_tti.get("Refund", {}).get("RefundDue", "0")

        # Upsert User Name if available
        user = db.query(models.User).filter(models.User.pan == pan).first()
        if user and personal_info:
             if not user.name or user.name == "Scraped User":
                first = personal_info.get("AssesseeName", {}).get("FirstName", "")
                last = personal_info.get("AssesseeName", {}).get("SurNameOrOrgName", "")
                user.name = f"{first} {last}".strip()
                db.add(user)

        # Upsert ITR Filing
        # Use acknowledgement number as the unique identifier
        # If ack_num is "Pending", generate a unique one from filename or use timestamp
        if ack_num == "Pending":
            # Generate a unique ID using AY + a hash of the JSON to avoid collisions
            import hashlib
            json_hash = hashlib.md5(json.dumps(itr_json).encode()).hexdigest()[:8]
            ack_num = f"PENDING-{ay}-{json_hash}"
        
        existing_itr = db.query(models.ITR_Filing).filter(
            models.ITR_Filing.ack_num == ack_num
        ).first()
        
        if existing_itr:
            existing_itr.ay = ay
            existing_itr.filing_date = filing_date
            existing_itr.total_income = total_income
            existing_itr.tax_payable = tax_payable
            existing_itr.itr_type = form_type
            existing_itr.refund_amount = str(refund)
            existing_itr.raw_data = json.dumps(itr_json)
        else:
            new_itr = models.ITR_Filing(
                user_pan=pan,
                ack_num=ack_num,
                ay=ay,
                filing_date=filing_date,
                total_income=total_income,
                tax_payable=tax_payable,
                itr_type=form_type,
                status="Filed",
                refund_amount=str(refund),
                raw_data=json.dumps(itr_json)
            )
            db.add(new_itr)
        
        # Run Rule Engine
        risks = rule_engine.evaluate_risks(itr_json)
        for risk in risks:
            # Dedup: Check if this risk title exists for this user/AY?
            # Risk model doesn't have AY. We should check if exact risk exists.
            exists = db.query(models.Risk).filter(
                models.Risk.user_pan == pan,
                models.Risk.title == risk['title'],
                models.Risk.description == risk['description']
            ).first()
            if not exists:
                db.add(models.Risk(user_pan=pan, **risk))
            
        opps = rule_engine.evaluate_opportunities(itr_json)
        for opp in opps:
            exists = db.query(models.Opportunity).filter(
                models.Opportunity.user_pan == pan,
                models.Opportunity.title == opp['title'],
                models.Opportunity.description == opp['description']
            ).first()
            if not exists:
                db.add(models.Opportunity(user_pan=pan, **opp))

        db.commit()
        return True, "Processed successfully"

    except Exception as e:
        logging.error(f"Error processing ITR: {e}")
        db.rollback()
        return False, str(e)
