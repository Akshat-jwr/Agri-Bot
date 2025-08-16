from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate
from app.schemas.auth import Token
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> dict:
        """Register new user"""
        # Check if user exists
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        new_user = await create_user(db, user_data)
        
        # Create access token
        access_token = create_access_token(data={"sub": new_user.email})
        
        return {
            "user_id": str(new_user.id),
            "email": new_user.email,
            "location": new_user.state_name,
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Token:
        """Authenticate user and return token"""
        # Demo users
        demo_users = {
            "demo@farmer.com": {"password": "demo123", "state": "Punjab"},
            "test@agri.com": {"password": "test123", "state": "Maharashtra"},
            "india@farmer.com": {"password": "india123", "state": "India"}
        }
        
        user = None
        
        # Check demo users
        if email in demo_users:
            demo = demo_users[email]
            if password == demo["password"]:
                user = await get_user_by_email(db, email)
                if not user:
                    # Create demo user
                    demo_user_data = UserCreate(email=email, password=password)
                    user = await create_user(db, demo_user_data)
                    user.state_name = demo["state"]
                    user.is_verified = True
                    await db.commit()
        else:
            # Check real users
            user = await get_user_by_email(db, email)
            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info={
                "user_id": str(user.id),
                "email": user.email,
                "location": user.state_name,
                "is_verified": user.is_verified
            }
        )
