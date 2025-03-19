# FastAPI-Template

fastapi 的模板，包含最基础的管理认证的等功能。

## 数据库管理

本项目使用 **alembic** 自动迁移数据库。每次修改数据库结构后要使用 **create_db_migration.py** 新建迁移脚本。

```shell
python create_db_migration.py
```

默认情况下启动程序会自动完成数据库的更新。可以通过修改 **config.py** 文件或者环境变量 **DATABASE_AUTO_UPGRADE** 控制是否需要自动更新。
