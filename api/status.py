from enum import Enum


class AdminpiStatus(Enum):
    OK = 0

    AdminStaffNotFound = 1001
    AdminStaffPasswordIncorrect = 1002
    AdminStaffCaptchaIncorrect = 1003
    AdminStaffBanned = 1004
    AdminStaffPasswordMisformed = 1005


class ApiStatus(Enum):
    OK = 0

    IncorrectPassword = 1001