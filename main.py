from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config.consul import read_config_by_key
from userapi.userapi import userapi_router
from adminpi.adminpi import adminpi_router

tags_metadata = [
    {
        "name": "api",
        "description": "用户端接口",
    },
    {
        "name": "adminpi",
        "description": "后台管理接口",
    },
]


app = FastAPI(title="后台模板", description="后台模板接口，分后台管理接口和用户端接口",
              version="0.0.1", contact={"name": "Wiky Lyu",
                                        "email": "admin@example.com", }, openapi_tags=tags_metadata,)

_http_config = read_config_by_key('http')

app.add_middleware(
    CORSMiddleware,
    allow_origins=_http_config['cors']['AllowOrigins'],
    allow_credentials=_http_config['cors']['AllowCredentials'],
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(SessionMiddleware,
                   secret_key=_http_config['session'], max_age=3600*24*30)

app.include_router(userapi_router, prefix='/api')  # 用户端接口
app.include_router(adminpi_router, prefix='/adminpi')  # 管理后台接口
