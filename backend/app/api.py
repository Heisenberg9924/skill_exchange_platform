from fastapi import APIRouter

from app.routes import auth_routes, chat_routes, exchange_request_routes, skill_routes, user_routes


api_router = APIRouter()
api_router.include_router(auth_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(skill_routes.router)
api_router.include_router(exchange_request_routes.router)
api_router.include_router(chat_routes.router)
