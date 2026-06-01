"""Users API routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, Any
from app.services.user_service import UserService
from app.database import get_session
from sqlalchemy.orm import Session

users_router = APIRouter()


class UserResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None


def _serialize_user(user: Any) -> dict:
    """Serialize Usuario model to JSON-friendly dict."""
    fecha_registro = getattr(user, "fecha_registro", None)
    return {
        "id": getattr(user, "id", None),
        "nombre": getattr(user, "nombre", None),
        "email": getattr(user, "email", None),
        "fecha_registro": fecha_registro.isoformat() if fecha_registro else None,
    }


@users_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(data: dict, session: Session = Depends(get_session)):
    """Create a new user"""
    try:
        user_service = UserService(session)
        user = user_service.create(data)
        return UserResponse(success=True, data=_serialize_user(user))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    finally:
        session.close()


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """Retrieve a user by ID"""
    try:
        user_service = UserService(session)
        user = user_service.get_by_id(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    finally:
        session.close()

    return UserResponse(success=True, data=_serialize_user(user))
