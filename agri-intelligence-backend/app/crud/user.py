from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, generate_verification_token
from typing import Optional
from datetime import datetime

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create new user with verification token"""
    hashed_password = get_password_hash(user.password)
    verification_token = generate_verification_token()
    
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        state_name="India",
        verification_token=verification_token,
        crops_of_interest=[],
        is_verified=False,  # Explicitly set to False
        is_active=True
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def verify_user_email(db: AsyncSession, verification_token: str) -> Optional[User]:
    """Verify user email with token"""
    result = await db.execute(
        select(User).where(User.verification_token == verification_token)
    )
    db_user = result.scalar_one_or_none()
    
    if db_user:
        db_user.is_verified = True
        db_user.verification_token = None  # Clear token after verification
        await db.commit()
        await db.refresh(db_user)
    
    return db_user

async def update_user(db: AsyncSession, user_id: str, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def regenerate_verification_token(db: AsyncSession, user: User) -> str:
    """Generate new verification token for existing user"""
    new_token = generate_verification_token()
    user.verification_token = new_token
    await db.commit()
    return new_token
