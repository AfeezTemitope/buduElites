"""
Custom DRF exception handler for consistent error responses.
All errors return: {"error": "...", "detail": {...}}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger("befa.errors")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "error": _get_error_message(response),
            "status_code": response.status_code,
        }
        response.data = error_data
    else:
        logger.exception("Unhandled exception: %s", exc)
        response = Response(
            {"error": "Internal server error", "status_code": 500},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return response


def _get_error_message(response):
    """Extract a human-readable error from DRF response data."""
    data = response.data
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        # Validation errors
        messages = []
        for field, errors in data.items():
            if isinstance(errors, list):
                messages.append(f"{field}: {', '.join(str(e) for e in errors)}")
            else:
                messages.append(f"{field}: {errors}")
        return "; ".join(messages) if messages else "An error occurred"
    if isinstance(data, list):
        return "; ".join(str(e) for e in data)
    return str(data)
