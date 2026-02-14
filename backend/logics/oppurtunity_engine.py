from .models import RawITR, UserProfile, OpportunityResult
from datetime import date

class OpportunityEngine:
    def __init__(self, itr: RawITR, profile: UserProfile):
        self.itr = itr
        self.profile = profile
        self.opportunities: List[OpportunityResult] = []
        self.current_year_deadline = f"March 31, {date.today().year + 1}" # Approx

    def calculate_opportunities(self) -> List[OpportunityResult]:
        self._analyze_80c_headroom()
        self._analyze_80d_health()
        self._analyze_nps()
        return self.opportunities

    def _analyze_80c_headroom(self):
        """
        Section 80C Limit: ₹1,50,000
        """
        limit = 150000
        claimed = self.itr.deductions_80c
        gap = limit - claimed
        
        if gap > 5000: # Ignore small gaps
            # Approx tax saving (30% slab assumed for impact visualization)
            savings = gap * 0.30
            
            self.opportunities.append(OpportunityResult(
                title="Maximize 80C",
                description=f"You have ₹{gap:,} unused in Section 80C limit. Consider ELSS or PPF.",
                deadline=self.current_year_deadline,
                savings_amount=savings
            ))

    def _analyze_80d_health(self):
        """
        Section 80D Limit: 
        - Self/Family: ₹25,000
        - Parents (>60): ₹50,000
        """
        # Logic for Parents
        if self.profile.parents_age > 60:
            parent_limit = 50000
            # Note: We need separate parent deduction data, assuming standard deduction logic here
            # For MVP, suggesting if total 80D is low
            if self.itr.deductions_80d < 25000: # Very low claim
                 self.opportunities.append(OpportunityResult(
                    title="Health Insurance for Parents",
                    description=f"Section 80D allows additional ₹{parent_limit:,} for senior citizen parents.",
                    deadline=self.current_year_deadline,
                    savings_amount=parent_limit * 0.30
                ))

    def _analyze_nps(self):
        """
        Section 80CCD(1B): Additional ₹50,000
        """
        if self.itr.deductions_80ccd_1b == 0:
            self.opportunities.append(OpportunityResult(
                title="NPS Contribution - 80CCD(1B)",
                description="Additional ₹50,000 investment in NPS qualifies for extra deduction.",
                deadline=self.current_year_deadline,
                savings_amount=50000 * 0.30
            ))