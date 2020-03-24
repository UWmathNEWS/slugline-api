from urllib.parse import urlparse, urlunparse

from rest_framework.pagination import LimitOffsetPagination
from common.response import Response


def to_relative_url(url):
    parse_result = urlparse(url)
    return urlunparse(
        (
            "",
            "",
            parse_result.path,
            parse_result.params,
            parse_result.query,
            parse_result.fragment,
        )
    )


class SluglinePagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response(
            super(SluglinePagination, self).get_paginated_response(data).data
        )

    def get_next_link(self):
        link = super().get_next_link()
        # remove the domain
        return to_relative_url(link)

    def get_previous_link(self):
        link = super().get_previous_link()
        return to_relative_url(link)
