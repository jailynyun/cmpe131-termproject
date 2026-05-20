from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.models.booking import User
from app.schemas.booking import UserCreate, UserUpdate, UserResponse

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse], summary="List all users")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of all users."""
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserResponse, summary="Get a user by ID")
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a single user by their ID."""
    db_user = db.query(User).filter(User.User_ID == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return db_user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    * Email must be unique.
    """
    db_user = User(**user.model_dump())
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Email '{user.Email}' is already registered.")
    db.refresh(db_user)
    return db_user


@router.patch("/{user_id}", response_model=UserResponse, summary="Update a user")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update one or more fields of an existing user."""
    db_user = db.query(User).filter(User.User_ID == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already in use by another account.")
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a user.
    * This will fail if the user has existing bookings — delete those first.
    """
    db_user = db.query(User).filter(User.User_ID == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    try:
        db.delete(db_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete user with existing bookings. Delete their bookings first.")
    return None
