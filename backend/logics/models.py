from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date

# --- Input Models (From Scraper) ---
class RawITR(BaseModel):
    ay: str
    filing_date: str
    gross_total_income: float
    total_deductions: float
    tax_paid: float
    refund_claimed: float
    # Specific Schedules
    salary_income: float = 0
    house_property_income: float = 0  # Rental Income
    capital_gains_stcg: float = 0
    capital_gains_ltcg: float = 0
    deductions_80c: float = 0
    deductions_80d: float = 0
    deductions_80ccd_1b: float = 0
    tds_claimed: float = 0

class RawAIS(BaseModel):
    rent_received: float = 0
    gross_salary: float = 0
    sale_of_securities: List[Dict] = [] # List of transaction dicts
    purchase_of_securities: List[Dict] = []
    total_tds_deposited: float = 0
    high_value_cash_deposits: float = 0

class UserProfile(BaseModel):
    pan: str
    age: int
    parents_age: int = 0
    risk_appetite: str # 'Conservative', 'Balanced', 'Aggressive'

# --- Output Models (For Frontend) ---
class RiskResult(BaseModel):
    type: str           # e.g., "Rental Income Documentation"
    severity: str       # "HIGH", "MEDIUM", "LOW"
    description: str
    impact_value: float # e.g., 48000
    action_item: str

class OpportunityResult(BaseModel):
    title: str
    description: str
    deadline: str
    savings_amount: float