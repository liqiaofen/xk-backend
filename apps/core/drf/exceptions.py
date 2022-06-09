from rest_framework.exceptions import APIException


class NotFoundException(APIException):
    status_code = 404
    default_detail = "Requested resource was not found."
    default_code = 'conflict'


class AppNotFoundError(Exception):
    pass
