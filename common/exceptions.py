from rest_framework.exceptions import APIException as _APIException


class APIException(_APIException):
    def __init__(self, detail, **kwargs):
        if isinstance(detail, str) or isinstance(detail, list):
            super().__init__(
                detail={"detail": [detail] if isinstance(detail, str) else detail},
                **kwargs
            )
        else:
            super().__init__(detail=detail, **kwargs)
