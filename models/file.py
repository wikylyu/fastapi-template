from sqlalchemy import Column, Integer, String

from models.base import BaseTable
from utils.uuid import uuidv4


class File(BaseTable):
    id: str = Column(String, primary_key=True, default=uuidv4)
    filename: str = Column(String, nullable=False, default="", comment="文件名称")
    content_type: str = Column(String, nullable=False, default="", comment="文件类型")
    size: int = Column(Integer, nullable=False, default=0, comment="文件大小，单位B")
    admin_user_id: int = Column(Integer, nullable=False, index=True, default=0)
