from django.core.exceptions import FieldError
from django.db.models import Q
from rest_framework import filters, settings
from common.search_parser import SearchParser

from functools import reduce


class SearchableFilterBackend(filters.BaseFilterBackend):
    """
    SearchableFilterBackend is a custom filter backend that allows searching of a queryset with GitHub-like syntax.
    A View that uses this backend provides two additional fields:

    - search_fields
        An array of field names that should be searched for regular search terms.
    - search_transformers (optional)
        A dict where the keys are possible user-provided field names, and the values are a function taking a query and
        returning a Q object. This can be used to process complex queries, or define convenience field names.

        If the `__term` key is defined in the provided dict, then regular search terms will be transformed with the
        corresponding function, and the search performed on the returned Q object instead of being done through
        `search_fields`.
    """

    __parser = SearchParser()
    __search_fields = None

    def filter_queryset(self, request, queryset, view):
        sort = request.query_params.get('sort', None)
        search = request.query_params.get('search', None)
        search_transformers = view.search_transformers if hasattr(view, "search_transformers") else {}

        # Cache fields so we don't have to recompute the map every time
        if self.__search_fields is None:
            self.__search_fields = map(lambda f: f + "__icontains", view.search_fields)

        if search is not None:
            parsed_terms, parsed_filters = self.__parser.parse_query(search)
            search_builder = []

            if "__term" in search_transformers:
                # Ignore default search fields if we have a transformer for search terms
                for term in parsed_terms:
                    search_builder.append(search_transformers["__term"](term))
            else:
                # Search each term in each field
                for field in self.__search_fields:
                    for term in parsed_terms:
                        search_builder.append(Q(**{field: term}))

            # Filter results
            for field, query in parsed_filters.items():
                if field in search_transformers:
                    search_builder.append(search_transformers[field](query[1]))
                    continue
                if query[0] == ":":
                    field = field + "__icontains"
                elif query[0] == "=":
                    field = field + "__iexact"
                search_builder.append(Q(**{field: query[1]}))

            if len(search_builder):
                try:
                    queryset = queryset.filter(reduce(lambda acc, f: acc | f, search_builder))
                except FieldError:
                    queryset = queryset.none()

        if sort is not None:
            queryset = queryset.order_by(sort)

        return queryset
