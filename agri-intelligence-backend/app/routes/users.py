from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.user import UserRead, UserUpdate
from app.schemas.response import APIResponse
from app.models.user import User
from app.crud.user import update_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """👤 Get my profile"""
    return current_user

@router.put("/me", response_model=APIResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✏️ Update my profile"""
    updated_user = await update_user(db, str(current_user.id), user_update)
    
    return APIResponse(
        message="Profile updated successfully",
        data={
            "user_id": str(updated_user.id),
            "state_name": updated_user.state_name,
            "district_name": updated_user.district_name,
            "crops_of_interest": updated_user.crops_of_interest
        }
    )
