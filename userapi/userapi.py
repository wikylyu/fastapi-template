from fastapi import APIRouter
from userapi.user import router as user_router

userapi_router = APIRouter()

userapi_router.include_router(user_router,prefix='/user')


