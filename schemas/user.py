from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    name: str
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None