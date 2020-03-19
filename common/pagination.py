from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class SluglinePagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "data": super(SluglinePagination, self)
                .get_paginated_response(data)
                .data,
            }
        )
