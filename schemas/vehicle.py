from pydantic import BaseModel
from typing import Optional


class Vehicle(BaseModel):
    brand: str
    model: str
    licence_plate: str
    type: str