
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text, Date
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    pan = Column(String, primary_key=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    email = Column(String)
    dob = Column(String) # DD-MM-YYYY format to match frontend
    created_at = Column(String, default=datetime.utcnow().isoformat())
    
    # Relationships
    itr_filings = relationship("ITR_Filing", back_populates="user")
    ais_entries = relationship("AIS_Entry", back_populates="user")
    risks = relationship("Risk", back_populates="user")
    opportunities = relationship("Opportunity", back_populates="user")
    advance_tax = relationship("AdvanceTax", back_populates="user")
    tds_entries = relationship("TDS_Entry", back_populates="user")
    notices = relationship("Notice", back_populates="user")

class ITR_Filing(Base):
    __tablename__ = "itr_filings"

    id = Column(Integer, primary_key=True, index=True)
    user_pan = Column(String, ForeignKey("users.pan"))
    ack_num = Column(String, unique=True, index=True)
    ay = Column(String)
    filing_date = Column(String)
    total_income = Column(Float)
    tax_payable = Column(Float)
    
    # New Fields for History Page
    itr_type = Column(String, default="ITR-1") # ITR-1, ITR-2, etc.
    status = Column(String, default="Filed") # Filed, Processed, Defective
    refund_amount = Column(String, default="0") # Stored as string to handle "—" or currency
    
    raw_data = Column(Text)
    
    user = relationship("User", back_populates="itr_filings")

class Notice(Base):
    __tablename__ = "notices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_pan = Column(String, ForeignKey("users.pan"))
    category = Column(String) # Notice / Order
    section = Column(String) # 143(1), 139(9)
    date = Column(String)
    description = Column(String)
    status = Column(String) # Pending, Resolved, Completed
    pdf_link = Column(String, nullable=True)
    
    user = relationship("User", back_populates="notices")

class AIS_Entry(Base):
    __tablename__ = "ais_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_pan = Column(String, ForeignKey("users.pan"))
    fy = Column(String)
    category = Column(String)
    description = Column(String)
    amount = Column(Float)
    source = Column(String)
    
    user = relationship("User", back_populates="ais_entries")

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    user_pan = Column(String, ForeignKey("users.pan"))
    ay = Column(String) # Added for Frontend
    risk_code = Column(String)
    title = Column(String) # mapped to 'wrong'
    severity = Column(String)
    description = Column(String) # mapped to 'why'
    amount_involved = Column(Float)
    solutions = Column(Text) # JSON List of strings ["Fix it", "Do this"]

    user = relationship("User", back_populates="risks")

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_pan = Column(String, ForeignKey("users.pan"))
    ay = Column(String) # Added for Frontend
    opp_code = Column(String)
    title = Column(String) # mapped to 'opportunity'
    description = Column(String)
    potential_savings = Column(Float) # mapped to 'savings'

    user = relationship("User", back_populates="opportunities")

class AdvanceTax(Base):
    __tablename__ = "advance_tax"

    id = Column(Integer, primary_key=True, index=True)
    user_pan = Column(String, ForeignKey("users.pan"))
    quarter = Column(String) # Q1, Q2, etc
    section = Column(String)
    due_date = Column(String)
    amount = Column(String) # Stored as string to keep currency symbol if needed, or float
    status = Column(String) # Paid, Pending, Upcoming
    reminder = Column(String)

    user = relationship("User", back_populates="advance_tax")

class TDS_Entry(Base):
    __tablename__ = "tds_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_pan = Column(String, ForeignKey("users.pan"))
    type = Column(String) # TDS / TCS
    section = Column(String)
    date = Column(String)
    tds_amount = Column(String)
    total_amount = Column(String)

    user = relationship("User", back_populates="tds_entries")
