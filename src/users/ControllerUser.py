from fastapi import APIRouter, HTTPException, status
from typing import Optional
import uuid

from src.users.services.UserService import UserService, UserCreate, UserRead, User

router = APIRouter()
user_service = UserService()  # Instantiate the UserService

@router.get("/all", response_model=list[UserRead])
async def read_all_users():
    """Read all users."""
    status_code, users = user_service.read_all_users()
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail="Failed to retrieve users.")
    return users

@router.get("/", response_model=Optional[UserRead])
async def read_user(user_id: uuid.UUID):
    """Read a user's details by user ID."""
    status_code, user = user_service.read_user(user_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user.")
    return user

@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate):
    """Create a new user."""
    status_code, user_read = user_service.create_user(User(**user.dict()))
    if status_code == 201:
        return user_read
    elif status_code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user: User ID already exists.")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user.")

@router.put("/", response_model=UserRead)
async def update_user(user_id: uuid.UUID, points: int):
    """Update user points."""
    status_code = user_service.update_user_points(user_id, points)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user points.")
    return {"detail": "User points updated successfully."}

@router.delete("/")
async def delete_user(user_id: uuid.UUID):
    """Delete a user."""
    status_code = user_service.delete_user(user_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user.")
    return {"detail": "User deleted successfully."}

@router.delete("/wipe", response_model=dict)
async def wipe_users():
    """Wipe all users from the database."""
    status_code = user_service.wipeClean()
    if status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to wipe users.")
    return {"detail": "All users wiped successfully."}
