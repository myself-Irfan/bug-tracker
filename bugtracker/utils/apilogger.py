from tracker.models import ApiLog


def _log(level, api_name, message, details=None, user=None, total_time=None):
    if details and not isinstance(details, str):
        try:
            details = str(details)
        except Exception:
            details = "Unserializable details"

    ApiLog.objects.create(
        api_name=api_name,
        level=level,
        message=message,
        details=details or "",
        user=user,
        total_time=total_time
    )

def info(api_name, message, details=None, user=None, total_time=None):
    _log(ApiLog.LevelChoice.INFO, api_name, message, details, user, total_time)

def warn(api_name, message, details=None, user=None, total_time=None):
    _log(ApiLog.LevelChoice.WARN, api_name, message, details, user, total_time)

def error(api_name, message, details=None, user=None, total_time=None):
    _log(ApiLog.LevelChoice.ERROR, api_name, message, details, user, total_time)

def fatal(api_name, message, details=None, user=None, total_time=None):
    _log(ApiLog.LevelChoice.FATAL, api_name, message, details, user, total_time)
