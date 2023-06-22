from pydantic import BaseModel


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
    return {'status': status, 'data': data}
