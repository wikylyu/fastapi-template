from enum import Enum


class ApiErrors(Enum):
    """api错误码"""

    OK = 0

    ADMIN_SUPERUSER_EXISTS = 1000
    ADMIN_USER_NOT_FOUND = 1001
    ADMIN_USER_PASSWORD_INCORRECT = 1002
    ADMIN_USER_BANNED = 1003


class ApiException(Exception):
    """自定义的exception"""

    def __init__(self, error: ApiErrors):
        self.error = error

    def __str__(self):
        return f"error: {self.error}"

    @property
    def status(self) -> int:
        return self.error.value
