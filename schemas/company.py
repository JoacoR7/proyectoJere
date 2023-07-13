from pydantic import BaseModel
from typing import Optional

class Company(BaseModel):
    id: Optional[int]
    name: str
