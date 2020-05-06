from django.db.models import Q
from rest_framework import filters, settings
from common.search_parser import SearchParser

from functools import reduce


class SearchableFilterBackend(filters.BaseFilterBackend):
    __parser = SearchParser()

    def filter_queryset(self, request, queryset, view):
        sort = request.query_params.get('sort', None)
        search = request.query_params.get('search', None)
        if search is not None:
            parsed_terms, parsed_filters = self.__parser.parse_query(search)
            search_terms = []
            search_filters = {}
            for field in map(lambda f: f + "__icontains", view.search_fields):
                for term in parsed_terms:
                    search_terms.append(Q(**{field: term}))
            for field, query in parsed_filters.items():
                if query[0] == ":":
                    field = field + "__icontains"
                elif query[0] == "=":
                    field = field + "__iexact"
                search_filters[field] = query[1]
            queryset = queryset.filter(**search_filters)
            if len(search_terms):
                queryset = queryset.filter(reduce(lambda acc, t: acc | t, search_terms))
        if sort is not None:
            queryset = queryset.order_by(sort)
        return queryset
