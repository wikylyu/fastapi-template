from datetime import datetime

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    updated_at: datetime
    created_at: datetime
    created_by: int = Field(default=0)

    class Config:
        from_attributes = True
