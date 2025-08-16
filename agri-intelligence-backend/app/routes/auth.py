from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import Token
from app.schemas.response import APIResponse
from app.services.auth_service import AuthService
from app.crud.user import verify_user_email

router = APIRouter()

@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    👤 **Register New User**
    
    **Example:**
    ```
    {
        "email": "farmer@example.com",
        "password": "mypassword123"
    }
    ```
    """
    try:
        result = await AuthService.register_user(db, user_data)
        return APIResponse(
            message="Registration successful! Welcome to Agricultural Intelligence.",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    🔐 **Login**
    
    **Demo accounts:**
    - Username: `demo@farmer.com`, Password: `demo123`
    - Username: `test@agri.com`, Password: `test123`
    """
    return await AuthService.authenticate_user(db, form_data.username, form_data.password)

@router.get("/verify/{verification_token}", response_model=APIResponse)
async def verify_email(
    verification_token: str,
    db: AsyncSession = Depends(get_db)
):
    """✅ Verify email address"""
    user = await verify_user_email(db, verification_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    return APIResponse(
        message="Email verified successfully!",
        data={"email": user.email, "verified": user.is_verified}
    )
