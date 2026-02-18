import json
import logging
from typing import List, Dict, Optional
from datetime import date

# ==========================================
# 1. Data Models (Standardized Objects)
# ==========================================

class RawITR:
    """Standardized ITR Data Object"""
    def __init__(self, ay, total_income, tax_payable, tax_paid, 
                 house_property_income=0, capital_gains_stcg=0, capital_gains_ltcg=0,
                 deductions_80c=0, deductions_80d=0, deductions_80ccd_1b=0, tds_claimed=0,
                 residential_status="RES", opt_out_new_regime="N"):
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
        self.residential_status = residential_status # "RES" or "NRI"
        self.opt_out_new_regime = opt_out_new_regime # "Y" (Old) or "N" (New)

class RawAIS:
    """Standardized AIS Data Object"""
    def __init__(self, rent_received=0, total_tds_deposited=0, sale_of_securities=None, interest_income=0):
        self.rent_received = float(rent_received)
        self.total_tds_deposited = float(total_tds_deposited)
        self.sale_of_securities = sale_of_securities if sale_of_securities else []
        self.interest_income = float(interest_income) # Savings + FD Interest

class RiskResult:
    """Standard Output for Risks"""
    def __init__(self, title, severity, description, amount_involved, solutions):
        self.title = title
        self.severity = severity
        self.description = description
        self.amount_involved = float(amount_involved)
        self.solutions = json.dumps(solutions) 

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
        def get_val(path, root=itr_json, default=0):
            val = root
            for key in path:
                if isinstance(val, dict):
                    val = val.get(key, {})
                else:
                    return default
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str) and val.replace('.','',1).isdigit():
                return float(val)
            return default

        def get_str(path, root=itr_json, default=""):
            val = root
            for key in path:
                val = val.get(key, {}) if isinstance(val, dict) else {}
            return str(val) if isinstance(val, str) else default

        itr_root = itr_json.get("ITR", {})
        form_type = next(iter(itr_root)) if itr_root else "Unknown"
        form_data = itr_root.get(form_type, {})

        # Default Values
        gross_total_income = 0.0
        tax_payable = 0.0
        tax_paid = 0.0
        hp_income = 0.0
        stcg = 0.0
        ltcg = 0.0
        ded_80c = 0.0
        ded_80d = 0.0
        ded_80ccd = 0.0
        tds_claimed = 0.0
        res_status = "RES"
        opt_out_new = "N"

        ay = form_data.get(f"Form_{form_type}", {}).get("AssessmentYear", "Unknown")

        if "ITR1" in form_type or "ITR4" in form_type:
            gross_total_income = get_val([f"{form_type}_IncomeDeductions", "GrossTotIncome"], form_data)
            tax_payable = get_val([f"{form_type}_TaxComputation", "NetTaxLiability"], form_data)
            tax_paid = get_val(["TaxPaid", "TaxesPaid", "TotalTaxesPaid"], form_data)
            hp_income = get_val([f"{form_type}_IncomeDeductions", "IncomeFromHP"], form_data)
            ded_80c = get_val([f"{form_type}_IncomeDeductions", "UsrDeductUndChapVIA", "Section80C"], form_data)
            tds_claimed = get_val(["TDS", "TotalTDSClaimed"], form_data)
            
            res_status = get_str(["FilingStatus", "ResidentialStatus"], form_data, "RES")
            opt_out_new = get_str(["FilingStatus", "OptOutNewTaxRegime"], form_data, "N")
            
        else:
            # ITR-2 / ITR-3
            gross_total_income = get_val(["PartB-TI", "GrossTotalIncome"], form_data)
            tax_payable = get_val(["PartB_TTI", "ComputationOfTaxLiability", "NetTaxLiability"], form_data)
            tax_paid = get_val(["PartB_TTI", "TaxPaid", "TaxesPaid", "TotalTaxesPaid"], form_data)
            
            hp_income = get_val(["ScheduleHP", "TotalIncomeHP"], form_data)
            stcg = get_val(["ScheduleCGFor23", "ShortTermCapGainFor23", "TotalSTCG"], form_data)
            ltcg = get_val(["ScheduleCGFor23", "LongTermCapGain23", "TotalLTCG"], form_data)
            
            via = form_data.get("ScheduleVIA", {}).get("UsrDeductUndChapVIA", {})
            ded_80c = get_val(["Section80C"], via)
            ded_80d = get_val(["Section80D"], via)
            ded_80ccd = get_val(["Section80CCD1B"], via)
            
            tds_claimed = get_val(["ScheduleTDS1", "TotalTDSClaimed"], form_data)
            
            filing_stat = form_data.get("PartA_GEN1", {}).get("FilingStatus", {})
            res_status = filing_stat.get("ResidentialStatus", "RES")
            opt_out_new = filing_stat.get("OptOutNewTaxRegime", "N")

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
            tds_claimed=tds_claimed,
            residential_status=res_status,
            opt_out_new_regime=opt_out_new
        )

    @staticmethod
    def normalize_ais(ais_list: list) -> RawAIS:
        ais = RawAIS()
        if not ais_list: return ais
        for entry in ais_list:
            try:
                category = entry.get("informationCategory", "") or entry.get("infoCategory", "")
                amount = float(entry.get("amount", 0) or 0)
                
                if "Rent received" in category:
                    ais.rent_received += amount
                elif "TDS" in category or "Tax Deducted" in category:
                    ais.total_tds_deposited += amount
                # --- NEW: Interest Income Check ---
                elif "Interest from savings" in category or "Interest from deposits" in category:
                    ais.interest_income += amount
                # ----------------------------------
                elif "Sale of securities" in category or "SFT-017" in category:
                    ais.sale_of_securities.append(entry)
            except Exception:
                continue
        return ais

# ==========================================
# 3. Risk Engine (The Muscle)
# ==========================================

from .ai_engine import AIEngine

class RiskEngine:
    def __init__(self, itr: RawITR, ais: RawAIS, user_profile: Optional[Dict] = None):
        self.itr = itr
        self.ais = ais
        self.profile = user_profile or {}
        self.risks = []
        self.ai = AIEngine()

    def execute(self) -> List["RiskResult"]:
        # Standard Math Checks
        self._check_rental_mismatch()
        self._check_capital_gains_misclass()
        self._check_tds_mismatch() # Covers Under & Over Claim
        self._check_interest_mismatch() # New Check
        self._check_high_income_disclosure()
        self._check_tax_liability_mismatch()
        
        # Questionnaire Checks
        self._check_residential_status_mismatch()
        self._check_declared_income_sources()

        # Enrich with AI
        for risk in self.risks:
            try:
                explanation = self.ai.generate_risk_explanation(
                    risk_data={
                        "title": risk.title,
                        "description": risk.description,
                        "amount_involved": risk.amount_involved,
                        "severity": risk.severity
                    },
                    user_profile=self.profile
                )
                
                current_solutions = json.loads(risk.solutions)
                current_solutions.append(f"AI Insight: {explanation}")
                risk.solutions = json.dumps(current_solutions)
            except Exception as e:
                pass 
                
        return self.risks

    def _check_rental_mismatch(self):
        if self.ais.rent_received > 0:
            diff = self.ais.rent_received - self.itr.house_property_income
            if diff > 50000:
                self.risks.append(RiskResult(
                    title="Rental Income Mismatch",
                    severity="High",
                    description=f"AIS shows ₹{self.ais.rent_received:,.0f} rent, but ITR declares only ₹{self.itr.house_property_income:,.0f}.",
                    amount_involved=diff,
                    solutions=["Reconcile with Form 26AS/AIS", "Revise Return"]
                ))

    def _check_capital_gains_misclass(self):
        risky_stcg = 0
        for txn in self.ais.sale_of_securities:
            desc = txn.get("description", "").lower()
            amt = float(txn.get("amount", 0))
            if "equity" in desc and "short term" in desc: 
                risky_stcg += amt
        
        if risky_stcg > 100000 and self.itr.capital_gains_stcg == 0:
             self.risks.append(RiskResult(
                title="Capital Gains Discrepancy",
                severity="Medium",
                description="AIS indicates Short Term Capital Gains which are missing in ITR.",
                amount_involved=risky_stcg,
                solutions=["Verify Broker Statement", "Report STCG in Schedule CG"]
            ))

    def _check_tds_mismatch(self):
        # 1. Under-Claim (You lost money)
        if self.ais.total_tds_deposited > (self.itr.tds_claimed + 1000):
            diff = self.ais.total_tds_deposited - self.itr.tds_claimed
            self.risks.append(RiskResult(
                title="Unclaimed TDS Credit",
                severity="Medium",
                description=f"You have ₹{diff:,.0f} unclaimed TDS appearing in AIS.",
                amount_involved=diff,
                solutions=["Update ITR to claim full TDS", "Check Form 26AS"]
            ))
            
        # 2. Over-Claim (You claimed too much - DANGEROUS)
        elif self.itr.tds_claimed > (self.ais.total_tds_deposited + 1000):
            diff = self.itr.tds_claimed - self.ais.total_tds_deposited
            self.risks.append(RiskResult(
                title="Mismatch in TDS claimed vs Form 26AS",
                severity="High",
                description=f"TDS amount claimed ₹{diff:,.0f} more than reflected in 26AS.",
                amount_involved=diff,
                solutions=["Revise Return immediately", "Pay the difference with interest", "Check for manual Challan entries"]
            ))

    def _check_interest_mismatch(self):
        # Check if AIS Interest exists but Total Income is suspiciously low or missing 'Other Sources' logic
        # For MVP, if AIS Interest > 0 and Total Income < AIS Interest (Implying it wasn't added)
        if self.ais.interest_income > 5000:
             if self.itr.total_income < self.ais.interest_income:
                 self.risks.append(RiskResult(
                    title="Interest income not declared",
                    severity="High",
                    description=f"FD/Savings interest of ₹{self.ais.interest_income:,.0f} from AIS not reported in ITR.",
                    amount_involved=self.ais.interest_income,
                    solutions=["Add Income from Other Sources", "Check Savings/FD Interest statement"]
                ))

    def _check_high_income_disclosure(self):
        if self.itr.total_income > 5000000:
            self.risks.append(RiskResult(
                title="High Income Disclosure",
                severity="Medium",
                description=f"Gross Total Income is ₹{self.itr.total_income:,.0f} (> ₹50L). Ensure 'Schedule AL' is filled.",
                amount_involved=self.itr.total_income,
                solutions=["Verify Schedule AL is filed", "Check for foreign assets"]
            ))

    def _check_tax_liability_mismatch(self):
        if self.itr.tax_payable > (self.itr.tax_paid + 100):
             diff = self.itr.tax_payable - self.itr.tax_paid
             self.risks.append(RiskResult(
                title="Outstanding Tax Demand",
                severity="High",
                description=f"Net Tax Liability (₹{self.itr.tax_payable:,.0f}) exceeds Taxes Paid (₹{self.itr.tax_paid:,.0f}).",
                amount_involved=diff,
                solutions=["Pay Self-Assessment Tax", "Check for challan mismatch"]
            ))

    # --- QUESTIONNAIRE CHECKS ---
    def _check_residential_status_mismatch(self):
        user_status = self.profile.get("residentialStatus", "")
        if user_status == "NRI" and "RES" in self.itr.residential_status:
             self.risks.append(RiskResult(
                title="Residential Status Mismatch",
                severity="High",
                description="You identified as NRI in the questionnaire, but your ITR was filed as Resident.",
                amount_involved=0,
                solutions=["File Revised Return as NRI", "Check 182-day rule"]
            ))

    def _check_declared_income_sources(self):
        sources = self.profile.get("income_sources", [])
        if "Capital Gains (Stocks/Property)" in sources:
            total_cg = self.itr.capital_gains_ltcg + self.itr.capital_gains_stcg
            if total_cg == 0:
                 self.risks.append(RiskResult(
                    title="Missing Capital Gains",
                    severity="Medium",
                    description="You indicated Capital Gains income in your profile, but Schedule CG in ITR is empty.",
                    amount_involved=0,
                    solutions=["Verify Capital Gains Report", "Check if gains were below basic exemption"]
                ))

# ==========================================
# 4. Opportunity Engine (The Savings)
# ==========================================

class OpportunityEngine:
    def __init__(self, itr: RawITR, user_profile: Optional[Dict] = None):
        self.itr = itr
        self.profile = user_profile or {}
        self.opportunities = []

    def execute(self) -> List[OpportunityResult]:
        user_regime = self.profile.get("newRegime", "")
        is_new_regime = "New Regime" in user_regime
        
        if not is_new_regime:
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
                potential_savings=gap * 0.30,
                opp_code="OPP_80C"
            ))

    def _check_80d(self):
        if self.itr.deductions_80d == 0:
            self.opportunities.append(OpportunityResult(
                title="Health Insurance (80D)",
                description="You haven't claimed Health Insurance. Save up to ₹25k (Self) + ₹50k (Parents).",
                potential_savings=25000 * 0.30,
                opp_code="OPP_80D"
            ))

    def _check_nps(self):
        if self.itr.deductions_80ccd_1b == 0:
            self.opportunities.append(OpportunityResult(
                title="NPS Contribution (80CCD 1B)",
                description="Invest ₹50,000 in NPS for additional deduction over and above 80C.",
                potential_savings=50000 * 0.30,
                opp_code="OPP_NPS"
            ))

# ==========================================
# 5. Public API Functions
# ==========================================

class TaxCalendarEngine:
    def __init__(self, itr: RawITR):
        self.itr = itr
        self.schedule = []

    def execute(self) -> List[Dict]:
        estimated_tax = self.itr.tax_paid * 1.10 
        today = date.today()
        year = today.year if today.month > 3 else today.year - 1
        
        deadlines = [
            {"quarter": "Q1", "due_date": f"{year}-06-15", "percent": 0.15},
            {"quarter": "Q2", "due_date": f"{year}-09-15", "percent": 0.45},
            {"quarter": "Q3", "due_date": f"{year}-12-15", "percent": 0.75},
            {"quarter": "Q4", "due_date": f"{year+1}-03-15", "percent": 1.00},
        ]
        
        results = []
        for item in deadlines:
            amount = estimated_tax * item['percent']
            status = "Upcoming"
            if today.strftime("%Y-%m-%d") > item['due_date']:
                status = "Overdue"
            
            results.append({
                "quarter": item['quarter'],
                "section": "234C",
                "due_date": item['due_date'],
                "amount": round(amount, 2),
                "status": status,
                "reminder": f"Pay {int(item['percent']*100)}% of tax by {item['due_date']}"
            })
        return results

def evaluate_risks(itr_json: dict, ais_data: list = None, user_profile: dict = None) -> list:
    try:
        raw_itr = DataNormalizer.normalize_itr(itr_json)
        raw_ais = DataNormalizer.normalize_ais(ais_data if ais_data else [])
        engine = RiskEngine(raw_itr, raw_ais, user_profile)
        risk_objects = engine.execute()
        return [vars(r) for r in risk_objects]
    except Exception as e:
        print(f"Risk Engine Error: {e}")
        return []

def evaluate_opportunities(itr_json: dict, user_profile: dict = None) -> list:
    try:
        raw_itr = DataNormalizer.normalize_itr(itr_json)
        engine = OpportunityEngine(raw_itr, user_profile)
        opp_objects = engine.execute()
        return [vars(o) for o in opp_objects]
    except Exception as e:
        print(f"Opp Engine Error: {e}")
        return []

def evaluate_tax_calendar(itr_json: dict) -> list:
    try:
        raw_itr = DataNormalizer.normalize_itr(itr_json)
        engine = TaxCalendarEngine(raw_itr)
        return engine.execute()
    except Exception as e:
        print(f"Tax Calendar Error: {e}")
        return []