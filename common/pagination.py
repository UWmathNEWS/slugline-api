from urllib.parse import urlparse, urlunparse

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def absolute_url_to_relative(url):
    result = urlparse(url)
    return urlunparse(
        ["", "", result.path, result.params, result.query, result.fragment]
    )


class SluglinePagination(PageNumberPagination):
    def get_next_link(self):
        return absolute_url_to_relative(super().get_next_link())

    def get_previous_link(self):
        return absolute_url_to_relative(super().get_previous_link())

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
