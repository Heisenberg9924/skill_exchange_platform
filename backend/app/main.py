from fastapi import FastAPI

from app.db.database import engine, Base
from app.models import user_model
from app.routes import auth_routes
from app.routes import user_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(user_routes.router)


@app.get("/")
def home():
    return {"message": "Backend Running"}