from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserSignup
from app.utils.hashing import hash_password
from app.utils.jwt import create_access_token
from app.utils.hashing import verify_password


def create_user(db: Session, user_data: UserSignup):

    # check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise Exception("Email already registered")

    # hash password
    hashed_pwd = hash_password(user_data.password)

    # create ORM object
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_pwd
    )

    # save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

from app.utils.jwt import create_access_token


def login_user(db: Session, email: str, password: str):

    # 1️⃣ find user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise Exception("Invalid email or password")

    # 2️⃣ verify password
    if not verify_password(password, str(user.hashed_password)):
        raise Exception("Invalid email or password")

    # 3️⃣ create token
    token = create_access_token(int(user.id))

    return token