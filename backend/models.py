from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal





class SalespersonBase(BaseModel):
    name: str
    region: str
    gps_location: str
    phone: str
    email: str

class SalespersonCreate(SalespersonBase):
    total_revenue: Optional[Decimal] = Decimal("0.00")
    monthly_target: Optional[Decimal] = Decimal("0.00")
    is_active: Optional[bool] = True

class Salesperson(SalespersonBase):
    id: str
    total_revenue: Decimal
    monthly_target: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DealerBase(BaseModel):
    name: str
    location: str
    contact_person: str
    phone: str
    email: str

class DealerCreate(DealerBase):
    status: Optional[str] = "active"

class Dealer(DealerBase):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class MeetingBase(BaseModel):
    salesperson_id: str
    dealer_id: Optional[str] = None
    notes: str
    outcome: str
    follow_up_date: Optional[datetime] = None
    location: str
    duration_minutes: int

class MeetingCreate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    name: str
    company: str
    phone: str
    email: str
    location: str
    source: str
    notes: str

class LeadCreate(LeadBase):
    status: Optional[str] = "new"
    score: Optional[int] = 50
    assigned_to: Optional[str] = None

class Lead(LeadBase):
    id: str
    status: str
    score: int
    assigned_to: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class LoginSessionBase(BaseModel):
    salesperson_id: str
    login_time: datetime
    location: Optional[str] = None
    device_info: Optional[str] = None

class LoginSessionCreate(LoginSessionBase):
    pass

class LoginSessionUpdate(BaseModel):
    logout_time: datetime

class LoginSession(LoginSessionBase):
    id: str
    logout_time: Optional[datetime] = None
    session_duration_minutes: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SalesRecordBase(BaseModel):
    salesperson_id: str
    sale_amount: Decimal
    product_name: str
    customer_name: str
    sale_date: datetime
    commission_rate: Optional[Decimal] = Decimal("0.10")

class SalesRecordCreate(SalesRecordBase):
    pass

class SalesRecord(SalesRecordBase):
    id: str
    commission_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True