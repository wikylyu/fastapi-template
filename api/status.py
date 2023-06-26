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

    UserBanned = 1000
    UserPasswordIncorrect = 1001
    PhoneCodeIncorrect = 1002
    PhoneCodeSentTooFast = 1003
    PhoneCodeSentFailure = 1004
    UserPhoneNotFound = 1005
