from rest_framework.response import Response as _Response


class Response(_Response):
    def __init__(self, data=None, success=True, **kwargs):
        super().__init__(data={
            'success': success,
            'data': data
        }, **kwargs)
