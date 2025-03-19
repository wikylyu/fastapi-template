import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APPNAME, APPVERSION, CORS_ALLOW_ORIGIN, DATABASE_AUTO_UPGRADE, ROOT_PATH
from middlewares.exception import ApiExceptionHandlingMiddleware
from routers import admin


async def run_db_upgrade():
    from alembic import command
    from alembic.config import Config

    # 设置 Alembic 配置文件的路径
    alembic_cfg = Config("alembic.ini")
    # 执行数据库迁移（升级到最新版本）

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
    print("Database has been upgraded.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if DATABASE_AUTO_UPGRADE:
            await run_db_upgrade()
    except Exception:
        traceback.print_exc()
    yield


app = FastAPI(title=APPNAME, version=APPVERSION, lifespan=lifespan, root_path=ROOT_PATH)

app.add_middleware(ApiExceptionHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOW_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router, prefix="/admin", tags=["Admin"])
