from rest_framework.renderers import JSONRenderer


class SluglineRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        rendered_json = {
            "success": True,
            "data": {**{k: v for k, v in data.items() if v is not None}},
        }
        return super().render(
            rendered_json,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context,
        )
