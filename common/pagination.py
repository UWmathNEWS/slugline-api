from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class SluglinePagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(
            data={
                "count": self.page.paginator.count,
                "page": self.page.number,
                "num_pages": self.page.paginator.num_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
