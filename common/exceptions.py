from rest_framework.exceptions import APIException


class SluglineAPIException(APIException):
    def __init__(self, detail):
        super().__init__(
            detail={
                "success": False,
                "error": [detail] if isinstance(detail, str) else detail,
            }
        )
