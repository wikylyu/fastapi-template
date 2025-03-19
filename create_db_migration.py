from datetime import datetime

from alembic import command
from alembic.config import Config
from config import DATABASE_URL


def main():
    # 设置 Alembic 配置文件的路径
    alembic_cfg = Config("alembic.ini")
    # 使用config的数据库配置，避免两个地方配置数据库
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

    today = datetime.today().strftime("%Y-%m-%d")
    # 执行数据库迁移（升级到最新版本）
    command.revision(alembic_cfg, message=today, autogenerate=True)


if __name__ == "__main__":
    main()
