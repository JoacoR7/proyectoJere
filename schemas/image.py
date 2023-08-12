from pydantic import BaseModel
from typing import Optional
from fastapi import File


class Image(BaseModel):
    case_id: int
    type: str
    validation_attemps: int
    metadata: str
    photo: str