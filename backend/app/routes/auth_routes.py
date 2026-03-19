from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserSignup, UserResponse, UserLogin
from app.services.auth_services import create_user, login_user
from app.utils.dependencies import get_db, get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/signup", response_model=UserResponse)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    new_user = create_user(db, user)
    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    token = login_user(db, user.email, user.password)
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(current_user = Depends(get_current_user)):
    # In a real application, you would handle token blacklisting here
    return {"message": "Logged out successfully"}

