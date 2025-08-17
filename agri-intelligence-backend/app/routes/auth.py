from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate
from app.schemas.auth import Token
from app.schemas.response import APIResponse
from app.services.auth_service import AuthService
from app.crud.user import verify_user_email

router = APIRouter()

@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    👤 **Register New User**
    
    **Required: Email verification before login**
    
    **Example:**
    ```
    {
        "email": "farmer@example.com",
        "password": "mypassword123"
    }
    ```
    
    **Flow:**
    1. Register with email and password
    2. Verification email sent automatically
    3. Click verification link in email
    4. Then you can login
    """
    try:
        result = await AuthService.register_user(db, user_data, background_tasks)
        return APIResponse(
            message="Registration successful! Please check your email and verify your account before logging in.",
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
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db)
):
    """
    🔐 **Login** (Email Verification Required)
    
    **Only verified users can login**
    
    **Demo accounts (auto-verified):**
    - Username: `demo@farmer.com`, Password: `demo123`
    - Username: `test@agri.com`, Password: `test123`
    
    **For regular users:**
    - Must verify email first
    - If unverified, new verification email will be sent
    """
    return await AuthService.authenticate_user(
        db, 
        form_data.username, 
        form_data.password, 
        background_tasks
    )

@router.get("/verify/{verification_token}", response_model=APIResponse)
async def verify_email(
    verification_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    ✅ **Verify Email Address**
    
    **Click the link from your verification email**
    
    After verification, you can login normally.
    """
    user = await verify_user_email(db, verification_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return APIResponse(
        message="🎉 Email verified successfully! You can now login to your account.",
        data={
            "email": user.email,
            "verified": user.is_verified,
            "login_url": "/api/v1/auth/login"
        }
    )

@router.post("/resend-verification", response_model=APIResponse)
async def resend_verification(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    📧 **Resend Verification Email**
    
    **Use this if you didn't receive the verification email**
    """
    from app.crud.user import get_user_by_email, regenerate_verification_token
    from app.services.email_service import EmailService
    
    user = await get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified. You can login now."
        )
    
    # Generate new token and send email
    new_token = await regenerate_verification_token(db, user)
    background_tasks.add_task(
        EmailService.send_verification_email,
        user.email,
        new_token
    )
    
    return APIResponse(
        message="Verification email resent. Please check your inbox.",
        data={"email": user.email}
    )
