from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Case(BaseModel):
    user_id: int
    company_id: int
    vehicle_id: int
    accident_number: int
    created_at: datetime
    finished_at: Optional[datetime]
    dropped: Optional[bool]
    policy: Optional[str]
    insured_name: Optional[str]
    insured_dni: Optional[str]
    insured_phone: str
    accident_date: Optional[datetime]
    accident_place: Optional[str]
    thef_type: Optional[str]