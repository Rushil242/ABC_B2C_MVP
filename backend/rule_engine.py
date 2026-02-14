
import json

def get_form_data(itr_data: dict):
    itr_root = itr_data.get("ITR", {})
    form_type = next(iter(itr_root)) if itr_root else "Unknown"
    return form_type, itr_root.get(form_type, {})

def evaluate_risks(itr_data: dict) -> list:
    """
    Analyzes ITR JSON and returns a list of Risk dictionaries.
    """
    risks = []
    
    try:
        form_type, form_data = get_form_data(itr_data)
        ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
        
        # Gross Income Extraction
        gross_income = 0
        if "ITR1" in form_type or "ITR4" in form_type:
            gross_income = form_data.get(f"{form_type}_IncomeDeductions", {}).get("GrossTotIncome", 0)
        else:
            gross_income = form_data.get("PartB-TI", {}).get("GrossTotalIncome", 0)
        
        # Rule 1: High Income Reporting
        if float(gross_income) > 5000000: # 50 Lakhs
            risks.append({
                "ay": ay,
                "risk_code": "HIGH_INC",
                "title": "High Income Disclosure",
                "severity": "Medium",
                "description": f"Gross Total Income is ₹{gross_income}, which is above ₹50 Lakhs. Ensure Assets & Liabilities schedule (Schedule AL) is filled.",
                "amount_involved": float(gross_income),
                "solutions": json.dumps(["Verify Schedule AL is filed", "Check for foreign assets"])
            })

        # Rule 2: Tax Liability Mismatch
        net_tax = 0
        taxes_paid = 0
        
        if "ITR1" in form_type or "ITR4" in form_type:
            net_tax = form_data.get(f"{form_type}_TaxComputation", {}).get("NetTaxLiability", 0)
            taxes_paid = form_data.get("TaxPaid", {}).get("TaxesPaid", {}).get("TotalTaxesPaid", 0)
        else:
            part_b_tti = form_data.get("PartB_TTI", {})
            net_tax = part_b_tti.get("ComputationOfTaxLiability", {}).get("NetTaxLiability", 0)
            taxes_paid = part_b_tti.get("TaxPaid", {}).get("TaxesPaid", {}).get("TotalTaxesPaid", 0)
        
        if float(net_tax) > float(taxes_paid):
            diff = float(net_tax) - float(taxes_paid)
            if diff > 100: # Ignore small rounding diffs
                risks.append({
                    "ay": ay,
                    "risk_code": "TAX_DUE",
                    "title": "Outstanding Tax Demand",
                    "severity": "High",
                    "description": f"Net Tax Liability (₹{net_tax}) exceeds Taxes Paid (₹{taxes_paid}).",
                    "amount_involved": float(diff),
                    "solutions": json.dumps(["Pay Self-Assessment Tax", "Check for challan mismatch"])
                })

    except Exception as e:
        print(f"Error in risk evaluation: {e}")
        import traceback
        traceback.print_exc()
        
    return risks

def evaluate_opportunities(itr_data: dict) -> list:
    """
    Analyzes ITR JSON and returns a list of Opportunity dictionaries.
    """
    opportunities = []
    
    try:
        form_type, form_data = get_form_data(itr_data)
        ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
        
        # Rule 1: Section 80C Utilization
        claim_80c = 0
        limit_80c = 150000
        
        if "ITR1" in form_type or "ITR4" in form_type:
            # ITR1 -> ITR1_IncomeDeductions -> UsrDeductUndChapVIA -> Section80C
            # OR ITR1 -> ITR1_IncomeDeductions -> DeductUndChapVIA -> Section80C (This is system calculated?)
            # Let's use UsrDeductUndChapVIA if available
            inc_ded = form_data.get(f"{form_type}_IncomeDeductions", {})
            claim_80c = inc_ded.get("UsrDeductUndChapVIA", {}).get("Section80C", 0)
        else:
            # ITR2 -> ScheduleVIA -> UsrDeductUndChapVIA -> Section80C
            schedule_via = form_data.get("ScheduleVIA", {}).get("UsrDeductUndChapVIA", {})
            claim_80c = schedule_via.get("Section80C", 0)
        
        if float(claim_80c) < limit_80c:
            potential = limit_80c - float(claim_80c)
            if potential > 5000: # Min threshold
                opportunities.append({
                    "ay": ay,
                    "opp_code": "OPP_80C",
                    "title": "Unclaimed Section 80C Deductions",
                    "description": f"You have claimed ₹{claim_80c} out of ₹{limit_80c}. You could save tax by investing more in PPF, ELSS, or LIC.",
                    "potential_savings": float(potential * 0.30) # Assuming 30% slab
                })
            
    except Exception as e:
        print(f"Error in opportunity evaluation: {e}")
        import traceback
        traceback.print_exc()
        
    return opportunities
