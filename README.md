# FastAPI-Template

这是一个基于 FastAPI 框架的后端项目模板，集成了常用的基础功能和最佳实践。

## 功能特点

- 基于 FastAPI 框架
- PostgreSQL 数据库支持
- Redis 缓存支持
- 用户认证和会话管理
- 验证码支持
- 自动数据库迁移（Alembic）
- CORS 跨域支持
- 环境变量配置
- 模块化的项目结构

## 项目结构

```
├── alembic/            # 数据库迁移相关文件
├── dal/                # 数据访问层
├── database/           # 数据库配置
├── middlewares/        # 中间件
├── models/            # 数据模型
├── routers/           # API路由
├── schemas/           # 数据验证模式
├── services/          # 业务逻辑层
├── utils/             # 工具函数
├── alembic.ini        # Alembic配置文件
├── config.py          # 项目配置
├── create_db_migration.py  # 数据库迁移脚本
├── main.py            # 应用入口
└── requirements.txt   # 项目依赖
```

## 环境要求

- Python 3.8+
- PostgreSQL
- Redis

## 安装

1. 克隆项目

```bash
git clone https://github.com/wikylyu/fastapi-template.git
cd fastapi-template
```

2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. 配置环境变量
   可以通过环境变量(如添加修改.env 文件)或修改 `config.py` 文件来配置项目：

- `APPNAME`: 应用名称
- `DATABASE_URL`: PostgreSQL 数据库连接 URL
- `REDIS_URL`: Redis 连接 URL
- `ROOT_PATH`: API 根路径
- `DEBUG`: 调试模式
- 更多配置请参考 `config.py`

## 数据库管理

本项目使用 Alembic 进行数据库迁移管理。

1. 创建新的迁移脚本：

```bash
python create_db_migration.py
```

2. 数据库更新：
   默认情况下，程序启动时会自动完成数据库的更新。可以通过修改 `config.py` 文件或设置环境变量 `DATABASE_AUTO_UPGRADE` 来控制是否需要自动更新。

## 启动服务

```bash
fastapi dev
```

服务启动后可访问：

- API 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

## License

MIT License
