from rest_framework import mixins
from rest_framework.response import Response


class RetrieveWithDetailModelMixin(mixins.RetrieveModelMixin):
    """
    A mixin for retrieve actions that includes detail fields as part of the response
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, use_detail=True)
        return Response(serializer.data)
