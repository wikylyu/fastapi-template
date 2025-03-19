from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from config import DATABASE_SCHEMA, DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    poolclass=NullPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
metadata_obj = MetaData(schema=DATABASE_SCHEMA)
Base = declarative_base(metadata=metadata_obj)
Session = scoped_session(SessionLocal)


def get_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        raise e
    finally:
        db.close()


get_db = contextmanager(get_session)
