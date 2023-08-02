from pydantic import BaseModel

class Business(BaseModel):
    name: str
    case_dropped_letter: str

class BusinessName(BaseModel):
    name: str
