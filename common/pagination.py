from rest_framework.pagination import LimitOffsetPagination
from common.response import Response


class SluglinePagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response(super(SluglinePagination, self).get_paginated_response(data).data)
