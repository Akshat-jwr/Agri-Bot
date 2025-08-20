from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks
from app.crud.user import get_user_by_email, create_user, regenerate_verification_token
from app.schemas.user import UserCreate
from app.schemas.auth import Token
from app.core.security import verify_password, create_access_token
from app.services.email_service import EmailService
from datetime import timedelta
from app.core.config import settings
import logging

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate, background_tasks: BackgroundTasks) -> dict:
        """Register new user and send verification email"""
        # Check if user exists
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            if existing_user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered and verified. Please login instead."
                )
            else:
                # User exists but not verified - resend verification but DO NOT raise error; return informative payload
                logging.info(f"[register] Unverified existing user {existing_user.email} requested registration -> resending token")
                new_token = await regenerate_verification_token(db, existing_user)
                background_tasks.add_task(
                    EmailService.send_verification_email,
                    existing_user.email,
                    new_token
                )
                return {
                    "user_id": str(existing_user.id),
                    "email": existing_user.email,
                    "already_registered": True,
                    "verification_resent": True,
                    "message": "Account already exists but is unverified. Verification email resent."
                }
        
        # Create new user
        logging.info(f"[register] Creating new user {user_data.email}")
        new_user = await create_user(db, user_data)
        
        # Send verification email
        background_tasks.add_task(
            EmailService.send_verification_email,
            new_user.email,
            new_user.verification_token
        )
        logging.info(f"[register] New user {new_user.email} created; verification email scheduled (token length={len(new_user.verification_token or '')})")
        
        return {
            "user_id": str(new_user.id),
            "email": new_user.email,
            "location": new_user.state_name,
            "verification_sent": True,
            "message": "Please check your email and verify your account before logging in."
        }
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        email: str, 
        password: str, 
        background_tasks: BackgroundTasks
    ) -> Token:
        """Authenticate user - only if verified"""
        # Demo users (always verified)
        demo_users = {
            "demo@farmer.com": {"password": "demo123", "state": "Punjab"},
            "test@agri.com": {"password": "test123", "state": "Maharashtra"},
            "india@farmer.com": {"password": "india123", "state": "India"}
        }
        
        user = None
        
        # Check demo users first
        if email in demo_users:
            demo = demo_users[email]
            if password == demo["password"]:
                user = await get_user_by_email(db, email)
                if not user:
                    # Create demo user
                    demo_user_data = UserCreate(email=email, password=password)
                    user = await create_user(db, demo_user_data)
                    user.state_name = demo["state"]
                    user.is_verified = True  # Demo users are auto-verified
                    user.verification_token = None
                    await db.commit()
        else:
            # Check regular users
            user = await get_user_by_email(db, email)
            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is verified (skip for demo users)
        if not user.is_verified and email not in demo_users:
            # Resend verification email
            if not user.verification_token:
                new_token = await regenerate_verification_token(db, user)
            else:
                new_token = user.verification_token
                
            background_tasks.add_task(
                EmailService.send_verification_email,
                user.email,
                new_token
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Verification email resent. Please verify your email before logging in.",
                headers={"X-Verification-Sent": "true"}
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
