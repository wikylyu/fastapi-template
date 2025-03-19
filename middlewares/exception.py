import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from routers.api import ApiException
from schemas.response import R


class ApiExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except ApiException as exc:
            response = JSONResponse(
                content=R.error(exc.error).to_json(),
            )
        except Exception:
            traceback.print_exc()
        return response
