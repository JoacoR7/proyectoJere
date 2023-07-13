from pydantic import BaseModel
from typing import Optional


class Vehicle(BaseModel):
    id: Optional[int]
    brand: str
    model: str
    licence_plate: str