from rest_framework.views import exception_handler


def slugline_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        arrayified_errors = {k: [v] if isinstance(v, str) else v for k, v in response.data.items()}
        response.data = {
            'success': False,
            'error': arrayified_errors
        }

    return response
