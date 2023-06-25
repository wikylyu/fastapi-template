from fastapi import APIRouter
from userapi.user import router as user_router

userapi_router = APIRouter(tags=['api'])

userapi_router.include_router(user_router, prefix='/user')
