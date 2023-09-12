from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas import vehicle

class Case(BaseModel):
    business_id: int
    vehicle: vehicle.Vehicle
    accident_number: str
    finished_at: Optional[datetime]
    dropped: Optional[bool]
    policy: Optional[str]
    insured_name: Optional[str]
    insured_dni: Optional[str]
    insured_phone: str
    accident_date: Optional[datetime]
    accident_place: Optional[str]
    thef_type: Optional[str]

class CaseModify(BaseModel):
    user_id: Optional[int]
    business_id: int
    vehicle: Optional[vehicle.Vehicle]
    accident_number: Optional[str]
    finished_at: Optional[datetime]
    dropped: Optional[bool]
    policy: Optional[str]
    insured_name: Optional[str]
    insured_dni: Optional[str]
    insured_phone: Optional[str]
    accident_date: Optional[datetime]
    accident_place: Optional[str]
    thef_type: Optional[str]    

class CaseId(BaseModel):
    case_id: int

class AccessToken(BaseModel):
    case_access_token: str
    case_id: str

class AccessTokenModify(BaseModel):
    case_access_token: str
    hour_from_now: Optional[int] = 0