from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import TypeVar, Generic, List
from api.status import ApiStatus, AdminpiStatus

T = TypeVar('T', bound=BaseModel)


class StatusResponse(GenericModel, Generic[T]):
    status: ApiStatus | AdminpiStatus
    data: T | None


class Pagination(GenericModel, Generic[T]):
    page: int = 1
    page_size: int = 10
    total: int = 0
    list: List[T] = []


class PaginationResponse(GenericModel, Generic[T]):
    status: ApiStatus | AdminpiStatus
    data: Pagination[T]


def success_response(data: any, cls: BaseModel | None = None, page: int | None = None, page_size: int | None = None, total: int | None = None):
    if data is None:
        pass
    elif page and page_size:
        data = {'list': [cls.from_orm(x) if cls else x for x in data],
                'page': page, 'page_size': page_size, 'total': total, }
    elif type(data) is list:
        data = [cls.from_orm(x) if cls else x for x in data]
    elif cls:
        data = cls.from_orm(data)
    return {'status': 0, 'data': data}


def failure_response(status: int, data: any = None):
    return StatusResponse(status=status, data=data)
    # return {'status': status, 'data': data}
