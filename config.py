import os

# App
APPNAME = os.getenv("APPNAME", "fastapi-template")
APPVERSION = os.getenv("APPVERSION", "0.0.1")
DEBUG = os.getenv("DEBUG", "True") == "True"

# HTTP
ROOT_PATH = os.getenv("ROOT_PATH", "/api")
CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://postgres@127.0.0.1:5432/{APPNAME.replace('-', '_')}")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "public")
DATABASE_TABLE_PREFIX = os.getenv("DATABASE_TABLE_PREFIX", "t_")  # 数据库前缀
DATABASE_AUTO_UPGRADE = os.getenv("DATABASE_AUTO_UPGRADE", "True") == "True"

# Admin

ADMIN_USERNAME_PATTERN = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
