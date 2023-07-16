from pydantic import BaseModel
from typing import Optional


class Image(BaseModel):
    id: Optional[int]
    case_id: int
    type: str
    validated: bool
    validation_attemps: int
    metadata: str