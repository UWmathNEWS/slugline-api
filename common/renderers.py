from rest_framework.renderers import JSONRenderer


class SluglineRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]
        if response.exception:
            # convert singular detail arguments into arrays
            if "detail" in data and isinstance(data["detail"], str):
                data["detail"] = [data["detail"]]
            # add a status code to the error object
            data["status_code"] = response.status_code
            rendered_json = {
                "success": False,
                "error": data,
            }
        else:
            rendered_json = {
                "success": True,
                "data": data,
            }
        return super().render(
            rendered_json,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context,
        )
