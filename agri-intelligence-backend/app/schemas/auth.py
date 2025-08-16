from pydantic import BaseModel, EmailStr
from typing import Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]

class TokenData(BaseModel):
    email: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
