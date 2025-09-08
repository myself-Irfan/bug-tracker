from rest_framework.views import exception_handler
from django.utils import timezone

from bugtracker.utils import apilogger
from tracker.exceptions.project_exceptions import ProjectServiceException


def custom_exception_handler(exc, context):
    """
    custom exception handler
    """

    response = exception_handler(exc, context)

    # context info
    request = context.get("request")
    view = context.get("view")
    user = getattr(request, "user", None)
    api_name = getattr(view, "api_name", "unknown_api")
    start_time = getattr(request, "_start_time", timezone.now())

    if response is not None:
        log_level = 'error' if response.status_code >= 500 else 'warning'

        if isinstance(exc, ProjectServiceException):
            log_details = f"{exc.message} | {exc.details}" if hasattr(exc, "details") and exc.details else str(exc)
        else:
            log_details = response.data

        log_method = getattr(apilogger, log_level)
        log_method(
            api_name=api_name,
            message='Response generated',
            details=log_details,
            user=user,
            total_time=(timezone.now() - start_time).total_seconds()
        )

    return response