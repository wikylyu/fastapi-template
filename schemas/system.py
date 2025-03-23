from pydantic import BaseModel


class Endpoint(BaseModel):
    method: str
    path: str
