from fastapi import APIRouter

from routers.userapi import auth

router = APIRouter()


router.include_router(auth.router, prefix="/auth", tags=["Auth"])
