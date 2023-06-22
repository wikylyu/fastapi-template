from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base,declared_attr
from sqlalchemy.orm import sessionmaker
from config.consul import read_config_by_key


_db_config = read_config_by_key('db')
_psql = create_engine(
    url=_db_config['psql']['dsn'],
    pool_size=25,
    max_overflow=50,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_psql)
Base = declarative_base()


class TableBase(Base):
    __abstract__=True
    _table_prefix="t_" # FIXME 修改数据表的前缀

    @declared_attr
    def __tablename__(cls):
        return cls._table_prefix + cls.__incomplete_tablename__

def get_psql():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        import traceback
        traceback.print_exception(e)
    finally:
        db.close()
