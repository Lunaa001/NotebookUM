"""Users API routes"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any
from app.services.user_service import UserService

users_router = APIRouter()
user_service = UserService()


class UserResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None


@users_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(data: dict):
    """Create a new user"""
    try:
        user = user_service.create(data)
        try:
            user_dict = user.to_dict()
        except AttributeError:
            user_dict = user
        return UserResponse(success=True, data=user_dict)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Retrieve a user by ID"""
    try:
        user = user_service.get_by_id(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    try:
        payload = user.to_dict()
    except AttributeError:
        payload = user

    return UserResponse(success=True, data=payload)
