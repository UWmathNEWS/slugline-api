from rest_framework import serializers


class ModelWithDetailSerializer(serializers.ModelSerializer):
    """
    A ModelWithDetailSerializer expands upon a ModelSerializer by granting the
    option to specify fields that only show up when the use_detail argument
    is provided.
    """

    def __init__(self, *args, **kwargs):
        use_detail = kwargs.pop("use_detail", False)
        detail_only_fields = getattr(self.Meta, "detail_fields", None)

        super().__init__(*args, **kwargs)

        if not use_detail and detail_only_fields is not None:
            for field_name in detail_only_fields:
                self.fields.pop(field_name)
