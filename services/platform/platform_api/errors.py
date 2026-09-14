from rest_framework.views import exception_handler as default_handler


def exception_handler(exc, context):
    response = default_handler(exc, context)
    if response is not None:
        detail = response.data.get("detail") if isinstance(response.data, dict) else None
        response.data = {"status": "error", "error_code": getattr(exc, "default_code", "REQUEST_FAILED").upper(),
                         "message": str(detail or "The request could not be completed.")}
        response["Cache-Control"] = "no-store"
    return response
