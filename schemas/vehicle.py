from pydantic import BaseModel
from typing import Optional


class Vehicle(BaseModel):
    brand: str
    model: str
    licence_plate: str
    type: str

class VehicleUpdate(BaseModel):
    brand: Optional[str]
    model: Optional[str]
    licence_plate: Optional[str]
    type: Optional[str]