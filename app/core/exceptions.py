from __future__ import annotations

import logging
from typing import Callable, Any

from app.core import http_exceptions
# from app.users.models import User  # noqa

logger = logging.getLogger("__name__")


def return_exception(error_status: int, details: str) -> http_exceptions:
    if error_status == 400:
        return http_exceptions.bad_format(details=details)
    elif error_status == 409:
        return http_exceptions.duplicate_record(details=details)
    elif error_status == 403:
        return http_exceptions.forbidden_action(details=details)
    elif error_status == 401:
        return http_exceptions.credential_exception(details=details)
    elif error_status == 422:
        return http_exceptions.unprocessable_entity(details=details)
    else:
        return http_exceptions.forbidden_action(details=details)


def monitor_crud_exceptions(
    module_path: str, function_name: str
) -> Callable[[Any], Any] | [None]:
    """
    This decorator ensure that the CRUD operations exceptions that might
    happen will be easily handled with an error message

    Currently only the following 3 exceptions are handled
        - syncpg.UniqueViolationError,
        - asyncpg.exceptions.NotNullViolationError,
        - asyncpg.exceptions.ForeignKeyViolationError,

    :param module_path: this is the path of the caller to be printed in the log
    :param function_name: this the decorated function's name to be printed in the log.
    :return:
    """

    def wrapped(func):
        async def run_and_monitor(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as error:
                error = error.__dict__
                logger.error(f"ERROR ON CRUD {error} ")

                error_status = error.get("status_code", 403)

                details = error.get("detail", "Impossible to register the action")
                logger.error(
                    "[{}] [{}] - Violated model constraint: {}".format(
                        module_path, function_name, error
                    ),
                    exc_info=False,
                )
                raise (return_exception(error_status=error_status, details=details))

        return run_and_monitor

    return wrapped
