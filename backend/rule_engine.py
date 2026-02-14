import json
import logging
from typing import List, Dict, Optional

# ==========================================
# 1. Data Models (Standardized Objects)
# ==========================================

class RawITR:
    """Standardized ITR Data Object"""
    def __init__(self, ay, total_income, tax_payable, tax_paid, 
                 house_property_income=0, capital_gains_stcg=0, capital_gains_ltcg=0,
                 deductions_80c=0, deductions_80d=0, deductions_80ccd_1b=0, tds_claimed=0):
        self.ay = ay
        self.total_income = float(total_income)
        self.tax_payable = float(tax_payable)
        self.tax_paid = float(tax_paid)
        self.house_property_income = float(house_property_income)
        self.capital_gains_stcg = float(capital_gains_stcg)
        self.capital_gains_ltcg = float(capital_gains_ltcg)
        self.deductions_80c = float(deductions_80c)
        self.deductions_80d = float(deductions_80d)
        self.deductions_80ccd_1b = float(deductions_80ccd_1b)
        self.tds_claimed = float(tds_claimed)

class RawAIS:
    """Standardized AIS Data Object"""
    def __init__(self, rent_received=0, total_tds_deposited=0, sale_of_securities=None):
        self.rent_received = float(rent_received)
        self.total_tds_deposited = float(total_tds_deposited)
        self.sale_of_securities = sale_of_securities if sale_of_securities else []

class RiskResult:
    """Standard Output for Risks"""
    def __init__(self, title, severity, description, amount_involved, solutions):
        self.title = title
        self.severity = severity
        self.description = description
        self.amount_involved = float(amount_involved)
        self.solutions = json.dumps(solutions) # Store as JSON string for DB

class OpportunityResult:
    """Standard Output for Opportunities"""
    def __init__(self, title, description, potential_savings, opp_code):
        self.title = title
        self.description = description
        self.potential_savings = float(potential_savings)
        self.opp_code = opp_code

# ==========================================
# 2. Data Normalizer (The Cleaner)
# ==========================================

class DataNormalizer:
    @staticmethod
    def normalize_itr(itr_json: dict) -> RawITR:
        # Helper to extract values safely from nested dicts
        def get_val(path, root=itr_json, default=0):
            val = root
            for key in path:
                if isinstance(val, dict):
                    val = val.get(key, {})
                else:
                    return default
            # Check if value is a number or string-number
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str) and val.replace('.','',1).isdigit():
                return float(val)
            return default

        # Determine Form Type
        itr_root = itr_json.get("ITR", {})
        form_type = next(iter(itr_root)) if itr_root else "Unknown"
        form_data = itr_root.get(form_type, {})

        # --- MAPPING LOGIC (Supports ITR-1, ITR-2, ITR-4) ---
        
        # 1. Basic Info
        ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")
        
        # 2. Income & Tax (Paths differ by form)
        if "ITR1" in form_type or "ITR4" in form_type:
            # Simplified Forms
            gross_total_income = get_val([f"{form_type}_IncomeDeductions", "GrossTotIncome"], form_data)
            tax_payable = get_val([f"{form_type}_TaxComputation", "NetTaxLiability"], form_data)
            tax_paid = get_val(["TaxPaid", "TaxesPaid", "TotalTaxesPaid"], form_data)
            
            # Specific Heads
            hp_income = get_val([f"{form_type}_IncomeDeductions", "IncomeFromHP"], form_data)
            ded_80c = get_val([f"{form_type}_IncomeDeductions", "UsrDeductUndChapVIA", "Section80C"], form_data)
            tds_claimed = get_val(["TDS", "TotalTDSClaimed"], form_data) 
        else:
            # ITR-2 / ITR-3 (Detailed Forms)
            gross_total_income = get_val(["PartB-TI", "GrossTotalIncome"], form_data)
            tax_payable = get_val(["PartB_TTI", "ComputationOfTaxLiability", "NetTaxLiability"], form_data)
            tax_paid = get_val(["PartB_TTI", "TaxPaid", "TaxesPaid", "TotalTaxesPaid"], form_data)
            
            # Specific Heads
            hp_income = get_val(["ScheduleHP", "TotalIncomeHP"], form_data)
            stcg = get_val(["ScheduleCGFor23", "ShortTermCapGainFor23", "TotalSTCG"], form_data)
            ltcg = get_val(["ScheduleCGFor23", "LongTermCapGain23", "TotalLTCG"], form_data)
            
            # Deductions
            via = form_data.get("ScheduleVIA", {}).get("UsrDeductUndChapVIA", {})
            ded_80c = get_val(["Section80C"], via)
            ded_80d = get_val(["Section80D"], via)
            ded_80ccd = get_val(["Section80CCD1B"], via)
            
            tds_claimed = get_val(["ScheduleTDS1", "TotalTDSClaimed"], form_data) 

        return RawITR(
            ay=ay,
            total_income=gross_total_income,
            tax_payable=tax_payable,
            tax_paid=tax_paid,
            house_property_income=hp_income,
            capital_gains_stcg=stcg if "ITR1" not in form_type else 0,
            capital_gains_ltcg=ltcg if "ITR1" not in form_type else 0,
            deductions_80c=ded_80c,
            deductions_80d=ded_80d if "ITR1" not in form_type else 0,
            deductions_80ccd_1b=ded_80ccd if "ITR1" not in form_type else 0,
            tds_claimed=tds_claimed
        )

    @staticmethod
    def normalize_ais(ais_list: list) -> RawAIS:
        ais = RawAIS()
        if not ais_list: return ais
        
        for entry in ais_list:
            try:
                # Handle potential key variations
                category = entry.get("informationCategory", "") or entry.get("infoCategory", "")
                amount = float(entry.get("amount", 0) or 0)
                
                if "Rent received" in category:
                    ais.rent_received += amount
                elif "TDS" in category or "Tax Deducted" in category:
                    ais.total_tds_deposited += amount
                elif "Sale of securities" in category or "SFT-017" in category:
                    ais.sale_of_securities.append(entry)
            except Exception:
                continue
                
        return ais

# ==========================================
# 3. Risk Engine (The Muscle)
# ==========================================

class RiskEngine:
    def __init__(self, itr: RawITR, ais: RawAIS):
        self.itr = itr
        self.ais = ais
        self.risks = []

    def execute(self) -> List[RiskResult]:
        self._check_rental_mismatch()
        self._check_capital_gains_misclass()
        self._check_tds_mismatch()
        self._check_high_income_disclosure()
        self._check_tax_liability_mismatch()
        return self.risks

    def _check_rental_mismatch(self):
        # Logic: If AIS Rent (Verified) > ITR Rent (Declared) + Threshold
        if self.ais.rent_received > 0:
            diff = self.ais.rent_received - self.itr.house_property_income
            if diff > 50000: # Threshold
                self.risks.append(RiskResult(
                    title="Rental Income Mismatch",
                    severity="High",
                    description=f"AIS shows ₹{self.ais.rent_received:,.0f} rent, but ITR declares only ₹{self.itr.house_property_income:,.0f}.",
                    amount_involved=diff,
                    solutions=["Reconcile with Form 26AS/AIS", "Revise Return"]
                ))

    def _check_capital_gains_misclass(self):
        # Logic: Detect short-term equity sales disguised as long-term or unreported
        risky_stcg = 0
        for txn in self.ais.sale_of_securities:
            desc = txn.get("description", "").lower()
            amt = float(txn.get("amount", 0))
            # Basic keyword check for MVP
            if "equity" in desc and "short term" in desc: 
                risky_stcg += amt
        
        # If AIS has significant STCG but ITR has 0 STCG
        if risky_stcg > 100000 and self.itr.capital_gains_stcg == 0:
             self.risks.append(RiskResult(
                title="Capital Gains Discrepancy",
                severity="Medium",
                description="AIS indicates Short Term Capital Gains which are missing in ITR.",
                amount_involved=risky_stcg,
                solutions=["Verify Broker Statement", "Report STCG in Schedule CG"]
            ))

    def _check_tds_mismatch(self):
        # Logic: Unclaimed TDS (AIS/26AS > ITR Claim)
        if self.ais.total_tds_deposited > (self.itr.tds_claimed + 1000):
            diff = self.ais.total_tds_deposited - self.itr.tds_claimed
            self.risks.append(RiskResult(
                title="Unclaimed TDS Credit",
                severity="Medium",
                description=f"You have ₹{diff:,.0f} unclaimed TDS appearing in AIS.",
                amount_involved=diff,
                solutions=["Update ITR to claim full TDS", "Check Form 26AS"]
            ))

    def _check_high_income_disclosure(self):
        # Logic: Income > 50L Check
        if self.itr.total_income > 5000000:
            self.risks.append(RiskResult(
                title="High Income Disclosure",
                severity="Medium",
                description=f"Gross Total Income is ₹{self.itr.total_income:,.0f} (> ₹50L). Ensure 'Schedule AL' is filled.",
                amount_involved=self.itr.total_income,
                solutions=["Verify Schedule AL is filed", "Check for foreign assets"]
            ))

    def _check_tax_liability_mismatch(self):
        # Logic: Tax Due vs Tax Paid
        if self.itr.tax_payable > (self.itr.tax_paid + 100): # 100 buffer
             diff = self.itr.tax_payable - self.itr.tax_paid
             self.risks.append(RiskResult(
                title="Outstanding Tax Demand",
                severity="High",
                description=f"Net Tax Liability (₹{self.itr.tax_payable:,.0f}) exceeds Taxes Paid (₹{self.itr.tax_paid:,.0f}).",
                amount_involved=diff,
                solutions=["Pay Self-Assessment Tax", "Check for challan mismatch"]
            ))

# ==========================================
# 4. Opportunity Engine (The Savings)
# ==========================================

class OpportunityEngine:
    def __init__(self, itr: RawITR):
        self.itr = itr
        self.opportunities = []

    def execute(self) -> List[OpportunityResult]:
        self._check_80c()
        self._check_80d()
        self._check_nps()
        return self.opportunities

    def _check_80c(self):
        limit = 150000
        gap = limit - self.itr.deductions_80c
        if gap > 5000:
            self.opportunities.append(OpportunityResult(
                title="Maximize 80C Deductions",
                description=f"You have claimed ₹{self.itr.deductions_80c:,.0f} out of ₹1.5L. Invest remaining to save tax.",
                potential_savings=gap * 0.30, # Assuming 30% bracket
                opp_code="OPP_80C"
            ))

    def _check_80d(self):
        # Basic check: If 0 claimed
        if self.itr.deductions_80d == 0:
            self.opportunities.append(OpportunityResult(
                title="Health Insurance (80D)",
                description="You haven't claimed Health Insurance. You can save up to ₹25k (Self) + ₹50k (Parents).",
                potential_savings=25000 * 0.30,
                opp_code="OPP_80D"
            ))

    def _check_nps(self):
        # Check Section 80CCD(1B) - Extra 50k
        if self.itr.deductions_80ccd_1b == 0:
            self.opportunities.append(OpportunityResult(
                title="NPS Contribution (80CCD 1B)",
                description="Invest ₹50,000 in NPS for additional deduction over and above 80C.",
                potential_savings=50000 * 0.30,
                opp_code="OPP_NPS"
            ))

# ==========================================
# 5. Public API Functions (Accessed by Service)
# ==========================================

def evaluate_risks(itr_json: dict, ais_data: list = None) -> list:
    """
    Main Entry Point for Risk Analysis.
    Converts Objects -> Dicts for backward compatibility with Service/API.
    """
    try:
        # 1. Normalize
        raw_itr = DataNormalizer.normalize_itr(itr_json)
        raw_ais = DataNormalizer.normalize_ais(ais_data if ais_data else [])
        
        # 2. Run Engine
        engine = RiskEngine(raw_itr, raw_ais)
        risk_objects = engine.execute()
        
        # 3. Convert to Dicts (for API response/DB storage)
        return [vars(r) for r in risk_objects]
        
    except Exception as e:
        print(f"Risk Engine Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def evaluate_opportunities(itr_json: dict) -> list:
    """
    Main Entry Point for Opportunity Analysis.
    """
    try:
        # 1. Normalize
        raw_itr = DataNormalizer.normalize_itr(itr_json)
        
        # 2. Run Engine
        engine = OpportunityEngine(raw_itr)
        opp_objects = engine.execute()
        
        # 3. Convert to Dicts
        return [vars(o) for o in opp_objects]
        
    except Exception as e:
        print(f"Opp Engine Error: {e}")
        return []