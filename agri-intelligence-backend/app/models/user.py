from sqlalchemy import Column, String, Boolean, JSON
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    state_name = Column(String(100), default="India", nullable=False)
    district_name = Column(String(100), nullable=True)
    crops_of_interest = Column(JSON, default=list)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
