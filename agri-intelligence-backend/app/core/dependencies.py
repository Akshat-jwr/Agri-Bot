from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_token
from app.crud.user import get_user_by_email
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_from_token(token: str, db: AsyncSession) -> User:
    """Get current authenticated user from direct token (for EventSource)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user
