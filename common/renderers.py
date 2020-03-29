from rest_framework.renderers import JSONRenderer


class SluglineRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context["response"].exception:
            rendered_json = {
                "success": False,
                "error": data,
            }
        else:
            rendered_json = {"success": True, "data": data}
        return super().render(
            rendered_json,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context,
        )
