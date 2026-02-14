from pydantic import BaseModel
from typing import List, Dict, Optional

# --- Internal Logic Models ---
class LogicITR(BaseModel):
    ay: str
    total_income: float
    tax_payable: float
    tax_paid: float
    refund_claimed: float
    house_property_income: float = 0
    capital_gains_stcg: float = 0
    capital_gains_ltcg: float = 0
    deductions_80c: float = 0
    deductions_80d: float = 0
    deductions_80ccd_1b: float = 0
    tds_claimed: float = 0

class LogicAIS(BaseModel):
    rent_received: float = 0
    gross_salary: float = 0
    total_tds_deposited: float = 0
    sale_of_securities: List[Dict] = []

class DataNormalizer:
    @staticmethod
    def normalize_itr(itr_json: dict) -> LogicITR:
        # Extract from ITR-2/3 structure or ITR-1
        # This is a simplified mapper. You'll need to map specific JSON paths based on ITR type.
        
        # Helper to safely get nested keys
        def get_val(path, default=0):
            val = itr_json
            for key in path:
                val = val.get(key, {})
            return float(val) if isinstance(val, (int, float, str)) and str(val).replace('.','').isdigit() else default

        # Example Mapping (Adjust based on your actual ITR JSON structure)
        root = itr_json.get("ITR", {}).get("ITR2", {}) # Assuming ITR2 for this example
        
        return LogicITR(
            ay=root.get("Form_ITR2", {}).get("AssessmentYear", "2024-25"),
            total_income=get_val(["ITR", "ITR2", "PartB-TI", "TotalIncome"]),
            tax_payable=get_val(["ITR", "ITR2", "PartB_TTI", "NetTaxLiability"]),
            tax_paid=get_val(["ITR", "ITR2", "PartB_TTI", "TaxPaid", "TaxesPaid", "TotalTaxesPaid"]),
            refund_claimed=get_val(["ITR", "ITR2", "PartB_TTI", "Refund", "RefundDue"]),
            
            # Specifics for Risk Engine
            house_property_income=get_val(["ITR", "ITR2", "ScheduleHP", "TotalIncomeHP"]),
            deductions_80c=get_val(["ITR", "ITR2", "ScheduleVIA", "UsrDeductUndChapVIA", "Section80C"]),
            tds_claimed=get_val(["ITR", "ITR2", "ScheduleTDS1", "TotalTDSClaimed"]) # Example path
        )

    @staticmethod
    def normalize_ais(ais_list: list) -> LogicAIS:
        """
        Converts list of AIS dicts into aggregated LogicAIS object.
        """
        ais_obj = LogicAIS()
        
        for entry in ais_list:
            category = entry.get("informationCategory", "")
            amount = float(entry.get("amount", 0))
            
            if "Rent received" in category:
                ais_obj.rent_received += amount
            elif "TDS" in category:
                ais_obj.total_tds_deposited += amount
            elif "Sale of securities" in category:
                ais_obj.sale_of_securities.append(entry)
                
        return ais_obj