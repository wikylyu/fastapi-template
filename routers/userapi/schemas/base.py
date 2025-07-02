from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    updated_at: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
