from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://backenduser:Rupdeep#2005@localhost:3306/skill_exchange"

engine = create_engine(DATABASE_URL, echo = True)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

Base = declarative_base()