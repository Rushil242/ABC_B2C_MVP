
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

        # Upsert User Name & DOB if available (Trust ITR data over registration data)
        user = db.query(models.User).filter(models.User.pan == pan).first()
        if user and personal_info:
            # Name
            first = personal_info.get("AssesseeName", {}).get("FirstName", "")
            mid = personal_info.get("AssesseeName", {}).get("MiddleName", "")
            last = personal_info.get("AssesseeName", {}).get("SurNameOrOrgName", "")
            
            full_name = f"{first} {mid} {last}".replace("  ", " ").strip()
            if full_name:
                user.name = full_name
            
            # DOB
            dob = personal_info.get("DOB")
            if dob:
                # Ensure format is DD-MM-YYYY or YYYY-MM-DD? User model expects String?
                # DB model usually String. ITR JSON DOB is usually YYYY-MM-DD or DD/MM/YYYY
                # Registration used DD-MM-YYYY.
                # Let's just save what we get, or normalize?
                # Frontend expects DD-MM-YYYY for Age calc?
                # Frontend code: const [d, m, y] = dob.split('-');
                # So it expects DD-MM-YYYY.
                # If ITR has YYYY-MM-DD, frontend breaks.
                # I should normalize to DD-MM-YYYY.
                try:
                    if "-" in dob:
                        parts = dob.split("-")
                        if len(parts[0]) == 4: # YYYY-MM-DD
                             dob = f"{parts[2]}-{parts[1]}-{parts[0]}"
                except:
                    pass
                user.dob = dob
            
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
        
        # 1. Fetch AIS Data for Risk Analysis (AY 2024-25 -> FY 2023-24)
        ais_entries = []
        try:
            # Parse AY (e.g., "2024-25" -> 2024, or "2024" -> 2024)
            if ay and ay != "Unknown":
                # Clean AY (remove 'PAY ' prefix if any, mainly handling simple year)
                ay_str = ay.split("-")[0].strip()
                if ay_str.isdigit():
                    ay_year = int(ay_str)
                    fy_year = ay_year - 1
                    fy = f"{fy_year}-{str(ay_year)[-2:]}"
                    
                    ais_records = db.query(models.AIS_Entry).filter(
                        models.AIS_Entry.user_pan == pan,
                        models.AIS_Entry.fy == fy
                    ).all()
                    
                    # Convert SQLAlchemy objects to list of dicts
                    for entry in ais_records:
                        ais_entries.append({
                            "informationCategory": entry.category,
                            "amount": entry.amount,
                            "description": entry.description,
                            "source": entry.source
                        })
        except Exception as e:
            logging.warning(f"Could not fetch AIS data for Rule Engine: {e}")

        risks = rule_engine.evaluate_risks(itr_json, ais_entries)
        for risk in risks:
            # Dedup: Check if this risk title exists for this user/AY?
            exists = db.query(models.Risk).filter(
                models.Risk.user_pan == pan,
                models.Risk.ay == ay,
                models.Risk.title == risk['title']
            ).first()
            if not exists:
                db.add(models.Risk(user_pan=pan, ay=ay, **risk))
            
        opps = rule_engine.evaluate_opportunities(itr_json)
        for opp in opps:
            exists = db.query(models.Opportunity).filter(
                models.Opportunity.user_pan == pan,
                models.Opportunity.ay == ay,
                models.Opportunity.title == opp['title']
            ).first()
            if not exists:
                db.add(models.Opportunity(user_pan=pan, ay=ay, **opp))
        
        # 4. Generate Advance Tax Schedule (New)
        adv_tax_schedule = rule_engine.evaluate_tax_calendar(itr_json)
        for tax in adv_tax_schedule:
            # Dedup based on quarter and section
            exists = db.query(models.AdvanceTax).filter(
                models.AdvanceTax.user_pan == pan,
                models.AdvanceTax.quarter == tax['quarter'],
                models.AdvanceTax.section == tax['section']
            ).first()
            
            if exists:
                # Update amount/status if changed
                exists.amount = str(tax['amount'])
                exists.status = tax['status']
                exists.due_date = tax['due_date']
                exists.reminder = tax.get('reminder', '')
            else:
                db.add(models.AdvanceTax(user_pan=pan, **tax))

        db.commit()
        return True, "Processed successfully"
    
    except Exception as e:
        logging.error(f"Error processing ITR: {e}")
        db.rollback()
        return False, str(e)
