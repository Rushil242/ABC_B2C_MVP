from sqlalchemy.orm import Session
from .. import models, rule_engine
import json
import logging

def process_itr_data(db: Session, pan: str, itr_json: dict):
    """
    Processes a single ITR JSON:
    1. Extracts key fields.
    2. Upserts ITR_Filing record.
    3. Runs Rule Engine to generate Risks/Opportunities.
    """
    try:
        # 1. Extract Fields (Same as before)
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
             ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
             personal_info = form_data.get("PersonalInfo", {})
             filing_status = form_data.get("FilingStatus", {})
             ack_num = filing_status.get("AcknowledgementNumber", filing_status.get("ReceiptNo", "Pending"))
             filing_date = filing_status.get("DateOfFiling", filing_status.get("OrigRetFiledDate", "Unknown"))
             if filing_date == "Unknown":
                 creation_info = form_data.get("CreationInfo", {})
                 filing_date = creation_info.get("JSONCreationDate", "Unknown")
             inc_ded = form_data.get(f"{form_type}_IncomeDeductions", {})
             total_income = float(inc_ded.get("TotalIncome", 0))
             tax_comp = form_data.get(f"{form_type}_TaxComputation", {})
             tax_payable = float(tax_comp.get("NetTaxLiability", 0))
             refund = form_data.get("Refund", {}).get("RefundDue", "0")
        else:
            ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
            personal_info = form_data.get("PartA_GEN1", {}).get("PersonalInfo", {})
            filing_status = form_data.get("PartA_GEN1", {}).get("FilingStatus", {})
            ack_num = filing_status.get("AcknowledgementNumber", filing_status.get("ReceiptNo", "Pending"))
            filing_date = filing_status.get("DateOfFiling", filing_status.get("OrigRetFiledDate", "Unknown"))
            if filing_date == "Unknown":
                creation_info = form_data.get("CreationInfo", {})
                filing_date = creation_info.get("JSONCreationDate", "Unknown")
            part_b_ti = form_data.get("PartB-TI", {})
            total_income = float(part_b_ti.get("TotalIncome", 0))
            part_b_tti = form_data.get("PartB_TTI", {})
            tax_payable = float(part_b_tti.get("NetTaxLiability", 0))
            refund = part_b_tti.get("Refund", {}).get("RefundDue", "0")

        # Upsert User Name & DOB if available
        user = db.query(models.User).filter(models.User.pan == pan).first()
        if user and personal_info:
            first = personal_info.get("AssesseeName", {}).get("FirstName", "")
            mid = personal_info.get("AssesseeName", {}).get("MiddleName", "")
            last = personal_info.get("AssesseeName", {}).get("SurNameOrOrgName", "")
            full_name = f"{first} {mid} {last}".replace("  ", " ").strip()
            if full_name: user.name = full_name
            
            dob = personal_info.get("DOB")
            if dob:
                try:
                    if "-" in dob:
                        parts = dob.split("-")
                        if len(parts[0]) == 4: # YYYY-MM-DD -> DD-MM-YYYY
                             dob = f"{parts[2]}-{parts[1]}-{parts[0]}"
                except: pass
                user.dob = dob
            db.add(user)

        # Upsert ITR Filing
        if ack_num == "Pending":
            import hashlib
            json_hash = hashlib.md5(json.dumps(itr_json).encode()).hexdigest()[:8]
            ack_num = f"PENDING-{ay}-{json_hash}"
        
        existing_itr = db.query(models.ITR_Filing).filter(models.ITR_Filing.ack_num == ack_num).first()
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
                user_pan=pan, ack_num=ack_num, ay=ay, filing_date=filing_date,
                total_income=total_income, tax_payable=tax_payable, itr_type=form_type,
                status="Filed", refund_amount=str(refund), raw_data=json.dumps(itr_json)
            )
            db.add(new_itr)
        
        # 4. Generate Advance Tax Schedule
        adv_tax_schedule = rule_engine.evaluate_tax_calendar(itr_json)
        for tax in adv_tax_schedule:
            exists = db.query(models.AdvanceTax).filter(
                models.AdvanceTax.user_pan == pan,
                models.AdvanceTax.quarter == tax['quarter'],
                models.AdvanceTax.section == tax['section']
            ).first()
            if exists:
                exists.amount = str(tax['amount'])
                exists.status = tax['status']
                exists.due_date = tax['due_date']
                exists.reminder = tax.get('reminder', '')
            else:
                db.add(models.AdvanceTax(user_pan=pan, **tax))

        db.commit()
        
        # 5. Run Rule Engine for User
        run_rules_for_user(db, pan)
        
        return True, "Processed successfully"
    
    except Exception as e:
        logging.error(f"Error processing ITR: {e}")
        db.rollback()
        return False, str(e)

def run_rules_for_user(db: Session, pan: str):
    """
    Runs the Rule Engine with Questionnaire Context.
    """
    try:
        # 1. Fetch Latest ITR
        itr_record = db.query(models.ITR_Filing).filter(models.ITR_Filing.user_pan == pan).order_by(models.ITR_Filing.ay.desc()).first()
        if not itr_record:
            return

        itr_json = json.loads(itr_record.raw_data)
        ay = itr_record.ay

        # 2. Fetch User Profile (Questionnaire Data)
        user = db.query(models.User).filter(models.User.pan == pan).first()
        user_profile = {}
        if user and user.questionnaire_data:
            try:
                user_profile = json.loads(user.questionnaire_data)
            except:
                user_profile = {}

        # 3. Fetch AIS Data
        ais_entries = []
        try:
             if ay and ay != "Unknown":
                ay_str = ay.split("-")[0].strip()
                if ay_str.isdigit():
                    ay_year = int(ay_str)
                    fy_year = ay_year - 1
                    fy = f"{fy_year}-{str(ay_year)[-2:]}"
                    
                    ais_records = db.query(models.AIS_Entry).filter(
                        models.AIS_Entry.user_pan == pan,
                        models.AIS_Entry.fy == fy
                    ).all()
                    
                    for entry in ais_records:
                        ais_entries.append({
                            "informationCategory": entry.category,
                            "amount": entry.amount,
                            "description": entry.description,
                            "source": entry.source
                        })
        except Exception:
            pass

        # 4. Run Rule Engine - Risks (PASS USER PROFILE)
        # Standard: Clear old risks for this AY/User before adding new ones
        db.query(models.Risk).filter(models.Risk.user_pan == pan, models.Risk.ay == ay).delete()
        
        risks = rule_engine.evaluate_risks(itr_json, ais_entries, user_profile=user_profile)
        
        for risk in risks:
            db.add(models.Risk(user_pan=pan, ay=ay, **risk))

        # 5. Run Rule Engine - Opportunities (PASS USER PROFILE)
        # Clear old opportunities
        db.query(models.Opportunity).filter(models.Opportunity.user_pan == pan, models.Opportunity.ay == ay).delete()

        opps = rule_engine.evaluate_opportunities(itr_json, user_profile=user_profile)
        
        for opp in opps:
            db.add(models.Opportunity(user_pan=pan, ay=ay, **opp))
        
        db.commit()
        logging.info(f"Rule Engine executed for {pan}")

    except Exception as e:
        logging.error(f"Rule Execution Failed for {pan}: {e}")