from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Your email address", example="farmer@example.com")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)", example="mypassword123")

class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    state_name: str
    district_name: Optional[str]
    crops_of_interest: List[str]
    is_active: bool
    is_verified: bool  # Show verification status
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    state_name: Optional[str] = Field(None, example="Punjab")
    district_name: Optional[str] = Field(None, example="Ludhiana")
    crops_of_interest: Optional[List[str]] = Field(None, example=["wheat", "rice"])
