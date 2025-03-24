from typing import Generic, TypeVar

from pydantic import BaseModel

from routers.api import ApiErrors

T = TypeVar("T")


class R(BaseModel, Generic[T]):
    status: int
    data: T | None = None

    @classmethod
    def success(cls, data: T):
        return cls(status=ApiErrors.OK.value, data=data)

    @classmethod
    def error(cls, error: ApiErrors):
        return cls(status=error.value, data=None)

    def to_json(self):
        return {"status": self.status, "data": self.data}


class P(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: list[T]

    @classmethod
    def from_list(cls, total: int, page: int, page_size: int, items: list[T]):
        return cls(total=total, page=page, page_size=page_size, items=items)
