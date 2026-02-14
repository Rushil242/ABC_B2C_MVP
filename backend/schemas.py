
from pydantic import BaseModel
from typing import List, Optional

# Auth Schemas
class LoginRequest(BaseModel):
    pan: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    pan: Optional[str] = None

class UserBase(BaseModel):
    pan: str
    name: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[str] = None # Added

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    personal_info: UserResponse
    address: Optional[str] = None
    phone: Optional[str] = None
    ao_details: Optional[dict] = None

# Dashboard Response Models
class RiskSchema(BaseModel):
    ay: Optional[str] = None
    title: str
    severity: str
    description: str
    amount_involved: float
    solutions: Optional[str] = None # JSON string
    class Config:
        orm_mode = True

class OpportunitySchema(BaseModel):
    ay: Optional[str] = None
    title: str
    description: str
    potential_savings: float
    class Config:
        orm_mode = True

class ITRSchema(BaseModel):
    ay: str
    filing_date: str
    total_income: float
    tax_payable: float
    class Config:
        orm_mode = True

class AdvanceTaxSchema(BaseModel):
    quarter: str
    section: str
    due_date: str
    amount: str
    status: str
    reminder: str
    class Config:
        orm_mode = True

class TDSSchema(BaseModel):
    type: str
    section: str
    date: str
    tds_amount: str
    total_amount: str
    class Config:
        orm_mode = True

class ITRHistorySchema(ITRSchema):
    itr_type: Optional[str] = "ITR-1"
    status: Optional[str] = "Filed"
    refund_amount: Optional[str] = "0"
    ack_num: Optional[str] = None
    
class NoticeSchema(BaseModel):
    category: str
    section: str
    date: str
    description: str
    status: str
    pdf_link: Optional[str] = None
    class Config:
        orm_mode = True

class DashboardResponse(BaseModel):
    user: UserResponse
    itr: Optional[ITRSchema]
    risks: List[RiskSchema]
    opportunities: List[OpportunitySchema]
    advance_tax: List[AdvanceTaxSchema]
    tds_tcs: List[TDSSchema]
