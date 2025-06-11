import os

from dotenv import load_dotenv

load_dotenv()

# App
APPNAME = os.getenv("APPNAME", "FastAPI 管理系统")
COPYRIGHT = os.getenv("COPYRIGHT", "© 2025 Wiky Lyu")
APPVERSION = os.getenv("APPVERSION", "0.0.1")
DEBUG = os.getenv("DEBUG", "True") == "True"

# HTTP
CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "CMDMwjPd1lfWpmqPpTlqyk9GFVJhW1PG")
SESSION_SECRET_NONCE = os.getenv("SESSION_SECRET_NONCE", "8Iz6FnZxeHH7")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres@127.0.0.1:5432/ft")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "public")
DATABASE_TABLE_PREFIX = os.getenv("DATABASE_TABLE_PREFIX", "t_")  # 数据库前缀
DATABASE_AUTO_UPGRADE = os.getenv("DATABASE_AUTO_UPGRADE", "True") == "True"

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

# Admin
ADMIN_USERNAME_PATTERN = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
