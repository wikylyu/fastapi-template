import asyncio
import time
import traceback
from contextlib import asynccontextmanager

from colorama import Fore, Style
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config import (
    APPNAME,
    APPVERSION,
    CORS_ALLOW_ORIGIN,
    DATABASE_AUTO_UPGRADE,
    DEBUG,
)
from middlewares.depends import get_client_real_ip
from middlewares.exception import ApiExceptionHandlingMiddleware
from routers import adminapi, userapi
from utils.time import get_short_time


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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    url = request.url

    client_ip = await get_client_real_ip(
        request,
        request.headers.get("X-Forwarded-For"),
        request.headers.get("X-Real-IP"),
        request.headers.get("CF-Connecting-IP"),
    )

    # 根据请求方法选择颜色
    method_colors = {
        "GET": Fore.GREEN,
        "POST": Fore.BLUE,
        "PUT": Fore.YELLOW,
        "DELETE": Fore.RED,
        "PATCH": Fore.CYAN,
        "OPTIONS": Fore.MAGENTA,
    }

    # 执行请求
    response = await call_next(request)

    def colored(text: str, color: str):
        return f"{color}{text}{Style.RESET_ALL}"

    # 计算处理时间
    process_time = (time.time() - start_time) * 1000
    # 根据状态码选择颜色
    method_color = method_colors.get(method, Fore.WHITE)
    status_color = Fore.GREEN if 200 <= response.status_code < 300 else Fore.RED

    readable_start_time = get_short_time(start_time)
    print(
        f"{colored(readable_start_time, Fore.LIGHTBLACK_EX)}: {colored(method, method_color)} {colored(url, Fore.LIGHTBLUE_EX)} - [{colored(response.status_code, status_color)}] [{process_time:.1f}ms] [{colored(client_ip, Fore.LIGHTBLACK_EX)}]"
    )

    return response
