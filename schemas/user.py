from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int]
    name: str
    username: str
    disabled_at: datetime = None
    password: str
    role: str