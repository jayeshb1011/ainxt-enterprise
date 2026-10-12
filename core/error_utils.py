"""
Shared helpers for safely surfacing exception information to API clients.

CodeQL (py/stack-trace-exposure) flags any code path where raw exception
text - which may contain internal file paths, SQL, stack frames, or other
implementation details - flows into an HTTP response. The helpers below
give callers a single, consistent way to:

  1. Always log the *full* exception (with traceback) server-side so nothing
     is lost for debugging/observability.
  2. Return a client-safe message: the real exception text in non-production
     environments (to keep local/dev debugging ergonomic), and a generic,
     non-identifying message in production so internals are never leaked to
     external users.
"""
from __future__ import annotations

from core.config import IS_PROD
from core.logger import logger

DEFAULT_GENERIC_MESSAGE = "An internal error occurred. Please try again or contact support."


def safe_error_detail(
    e: BaseException,
    context: str = "",
    generic: str = DEFAULT_GENERIC_MESSAGE,
) -> str:
    """
    Log ``e`` with full traceback and return a message safe to send to clients.

    In non-production environments the original exception message is
    returned so developers retain the detail they're used to. In production
    (``IS_PROD`` True) a generic message is returned instead so stack traces,
    paths, queries, etc. are never exposed to external callers.

    Args:
        e: The caught exception.
        context: Optional short description of where/what failed, used only
            in the server-side log line (never returned to the client).
        generic: Optional override for the production-safe message.

    Returns:
        A string suitable for use as an HTTP error ``detail``/``error`` field.
    """
    log_msg = f"{context}: {e}" if context else str(e)
    logger.error(log_msg, exc_info=True)
    if IS_PROD:
        return generic
    return str(e)
