from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserProfileUpdate, UserSignup
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token


def create_user(db: Session, user_data: UserSignup) -> User:
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        bio=user_data.bio,
        profile_photo_url=(
            str(user_data.profile_photo_url) if user_data.profile_photo_url else None
        ),
        city=user_data.city,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


def login_user(db: Session, email: str, password: str) -> dict[str, str | User]:
    user = authenticate_user(db, email, password)
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}


def update_user_profile(db: Session, user: User, payload: UserProfileUpdate) -> User:
    update_data = payload.model_dump(exclude_unset=True)

    if "profile_photo_url" in update_data and update_data["profile_photo_url"] is not None:
        update_data["profile_photo_url"] = str(update_data["profile_photo_url"])

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
