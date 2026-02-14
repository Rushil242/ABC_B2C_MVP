
import json

def evaluate_risks(itr_data: dict) -> list:
    """
    Analyzes ITR JSON and returns a list of Risk dictionaries.
    Each dict should match the keys required for models.Risk (except user_pan).
    """
    risks = []
    
    try:
        # Navigate JSON safely
        itr2 = itr_data.get("ITR", {}).get("ITR2", {})
        ay = itr2.get("Form_ITR2", {}).get("AssessmentYear", "Unknown")
        
        # Rule 1: High Income Reporting
        part_b_ti = itr2.get("PartB-TI", {})
        gross_income = part_b_ti.get("GrossTotalIncome", 0)
        
        if gross_income > 5000000: # 50 Lakhs
            risks.append({
                "ay": ay,
                "risk_code": "HIGH_INC",
                "title": "High Income Disclosure",
                "severity": "Medium",
                "description": f"Gross Total Income is ₹{gross_income}, which is above ₹50 Lakhs. Ensure Assets & Liabilities schedule (Schedule AL) is filled.",
                "amount_involved": float(gross_income),
                "solutions": json.dumps(["Verify Schedule AL is filed", "Check for foreign assets"])
            })

        # Rule 2: Tax Liability Mismatch (Simple check)
        part_b_tti = itr2.get("PartB_TTI", {})
        net_tax = part_b_tti.get("ComputationOfTaxLiability", {}).get("NetTaxLiability", 0)
        taxes_paid = part_b_tti.get("TaxPaid", {}).get("TaxesPaid", {}).get("TotalTaxesPaid", 0)
        
        if net_tax > taxes_paid:
            diff = net_tax - taxes_paid
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
        
    return risks

def evaluate_opportunities(itr_data: dict) -> list:
    """
    Analyzes ITR JSON and returns a list of Opportunity dictionaries.
    """
    opportunities = []
    
    try:
        itr2 = itr_data.get("ITR", {}).get("ITR2", {})
        ay = itr2.get("Form_ITR2", {}).get("AssessmentYear", "Unknown")
        
        # Rule 1: Section 80C Utilization
        # Note: In new regime, this might not apply, but keeping logic simple for MVP.
        schedule_via = itr2.get("ScheduleVIA", {}).get("UsrDeductUndChapVIA", {})
        claim_80c = schedule_via.get("Section80C", 0)
        limit_80c = 150000
        
        if claim_80c < limit_80c:
            potential = limit_80c - claim_80c
            opportunities.append({
                "ay": ay,
                "opp_code": "OPP_80C",
                "title": "Unclaimed Section 80C Deductions",
                "description": f"You have claimed ₹{claim_80c} out of ₹{limit_80c}. You could save tax by investing more in PPF, ELSS, or LIC.",
                "potential_savings": float(potential * 0.30) # Assuming 30% slab
            })
            
    except Exception as e:
        print(f"Error in opportunity evaluation: {e}")
        
    return opportunities
