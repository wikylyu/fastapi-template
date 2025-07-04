import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    APPNAME,
    APPVERSION,
    CORS_ALLOW_ORIGIN,
    DATABASE_AUTO_UPGRADE,
    DEBUG,
)
from middlewares.exception import ApiExceptionHandlingMiddleware
from routers import adminapi, userapi


async def run_db_upgrade():
    from alembic import command
    from alembic.config import Config

    # 设置 Alembic 配置文件的路径
    alembic_cfg = Config("alembic.ini")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
    print("Database migration completed successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if DATABASE_AUTO_UPGRADE:
            await run_db_upgrade()
    except Exception:
        traceback.print_exc()
    yield


app = FastAPI(title=APPNAME, version=APPVERSION, lifespan=lifespan, debug=DEBUG)

app.add_middleware(ApiExceptionHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOW_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(adminapi.router, prefix="/adminapi")
app.include_router(userapi.router, prefix="/api")
