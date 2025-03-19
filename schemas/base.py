from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
