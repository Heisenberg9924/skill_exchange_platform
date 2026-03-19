from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable = False)
    email = Column(String(100), unique=True, index = True, nullable=False)
    hashed_password = Column(String(255), nullable = False)
    bio = Column(String(255), nullable=True)
    profile_photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    