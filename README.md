# FastAPI 管理系统

FastAPI 管理系统是一个使用 Python 语言和 FastAPI 框架构建的后台管理系统。

## 项目特点

- 使用 FastAPI 框架，提供了高性能的 API 服务
- 使用 SQLAlchemy 作为 ORM 工具，支持多种数据库
- 使用 Redis 作为缓存工具，提供了高效的缓存机制
- 使用 Pydantic 作为数据模型工具，提供了强大的数据模型定义和验证功能
- 使用 Alembic 作为数据库迁移工具，提供了便捷的数据库迁移功能
- 使用 CAPTCHA 图形验证码，提供了防止机器人攻击的功能

## 项目结构

- `app` - FastAPI 项目主目录
- `app/adminapi` - 管理 API router
- `app/adminapi/auth.py` - 管理 API 认证路由
- `app/adminapi/admin.py` - 管理 API 用户路由
- `app/adminapi/system.py` - 管理 API 系统路由
- `app/models` - 数据模型目录
- `app/models/admin.py` - 管理用户模型
- `app/models/system.py` - 系统模型
- `app/routers` - 路由目录
- `app/routers/adminapi` - 管理 API 路由
- `app/routers/response.py` - 路由响应工具
- `app/services` - 服务目录
- `app/services/encrypt.py` - 加密服务
- `app/utils` - 工具目录
- `app/utils/password.py` - 密码工具
- `app/utils/string.py` - 字符串工具
- `app/utils/uuid.py` - UUID 工具
- `config.py` - 配置文件
- `requirements.txt` - 依赖项文件

## 快速开始

1. 安装依赖项 `pip install -r requirements.txt`
2. 创建数据库和表结构 `python create_db_migration.py`
3. 启动 FastAPI 服务 `fastapi dev`
4. 访问 FastAPI 服务 `http://localhost:8000/`
