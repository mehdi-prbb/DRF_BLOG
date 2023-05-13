from rest_framework.exceptions import APIException


class DuplicatePhoneNumberException(APIException):
    status_code = 406
    default_detail = 'duplicate phone number'
    default_code = 'duplicate exception'