from pydantic import BaseModel
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class EmailChangeRequest(BaseModel):
    new_email: str

class EmailChangeConfirm(BaseModel):
    new_email: str
    code: str

class ArrangementOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    category_id: Optional[int] = None
    views: int = 0
    photos: List[str]
    created_at: str
