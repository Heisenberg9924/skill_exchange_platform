from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user_schema import (
    AuthTokenResponse,
    MessageResponse,
    UserLogin,
    UserResponse,
    UserSignup,
)
from app.services.auth_services import create_user, login_user
from app.utils.dependencies import get_current_user, get_db


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/login", response_model=AuthTokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user.email, user.password)


@router.post("/logout", response_model=MessageResponse)
def logout(current_user=Depends(get_current_user)):
    return {"message": f"User {current_user.email} logged out successfully"}
