from typing import List
# Assuming RawITR and RawAIS are defined in normalization or models
from .normalization import RawITR, RawAIS 

class RiskResult:
    def __init__(self, type, severity, description, impact_value, action_item):
        self.type = type
        self.severity = severity
        self.description = description
        self.impact_value = impact_value
        self.action_item = action_item

class RiskEngine:
    def __init__(self, itr: RawITR, ais: RawAIS):
        self.itr = itr
        self.ais = ais
        self.risks: List[RiskResult] = []

    def execute_all_checks(self) -> List[RiskResult]:
        self._check_rental_mismatch()
        self._check_capital_gains_classification()
        self._check_tds_mismatch()
        return self.risks

    def _check_rental_mismatch(self):
        """
        Logic: Checks if Rent declared in ITR matches Rent in AIS.
        Threshold: ₹50,000 difference triggers risk.
        """
        declared_rent = self.itr.house_property_income
        actual_rent = self.ais.rent_received
        
        diff = abs(declared_rent - actual_rent)
        
        # If AIS shows rent but ITR shows significantly less (or zero)
        if actual_rent > 0 and diff > 50000:
            tax_impact = diff * 0.30  # Est. 30% slab
            
            self.risks.append(RiskResult(
                type="Rental Income Documentation",
                severity="HIGH",
                description=f"AIS shows rent of ₹{actual_rent:,}, but ITR declares ₹{declared_rent:,}. Mismatch of ₹{diff:,}.",
                impact_value=tax_impact,
                action_item="Reconcile with Tenant's Form 16C and update ITR."
            ))

    def _check_capital_gains_classification(self):
        """
        Logic: Detects if Short Term Gains (High Tax) are misclassified as Long Term (Low Tax).
        """
        risky_stcg_amount = 0
        
        # Scan AIS transactions for Equity sold within 12 months
        for txn in self.ais.sale_of_securities:
            # We assume the Normalizer/Scraper has calculated 'holding_period_days' or we infer it
            # For MVP, if 'holding_period' is missing, we skip.
            is_equity = "Equity" in txn.get("description", "") or txn.get("asset_type") == "Equity"
            holding_days = txn.get("holding_period_days", 0) # Needs smart scraper logic
            
            if is_equity and 0 < holding_days < 365:
                risky_stcg_amount += float(txn.get("amount", 0))

        # Trigger Risk: If AIS sees Short Term sales, but ITR claims 0 Short Term and High Long Term
        if risky_stcg_amount > 100000 and self.itr.capital_gains_stcg == 0 and self.itr.capital_gains_ltcg > 0:
            tax_diff = risky_stcg_amount * (0.15 - 0.10) # 15% STCG vs 10% LTCG
            
            self.risks.append(RiskResult(
                type="Capital Gains Classification",
                severity="MEDIUM",
                description="Potential misclassification: AIS shows Short Term equity sales, but ITR claims Long Term.",
                impact_value=tax_diff,
                action_item="Verify holding periods for equity transactions."
            ))

    def _check_tds_mismatch(self):
        """
        Logic: Checks if user forgot to claim TDS credits shown in 26AS/AIS.
        """
        if self.ais.total_tds_deposited > (self.itr.tds_claimed + 1000): # 1000 buffer
            diff = self.ais.total_tds_deposited - self.itr.tds_claimed
            self.risks.append(RiskResult(
                type="Unclaimed TDS Credit",
                severity="MEDIUM",
                description=f"You have unclaimed TDS credit of ₹{diff:,} appearing in AIS/26AS.",
                impact_value=diff,
                action_item="Update ITR to claim full TDS credit."
            ))