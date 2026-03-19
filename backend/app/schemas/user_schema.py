from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserSignup(BaseModel):
    name : str
    email : EmailStr
    password : str
    bio : Optional[str] = None
    profile_photo_url : Optional[str] = None

class UserLogin(BaseModel):
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    id : int
    name : str
    email : EmailStr
    bio : Optional[str] = None
    profile_photo_url : Optional[str] = None
    created_at : datetime
    updated_at : datetime

    class Config:
        orm_mode = True