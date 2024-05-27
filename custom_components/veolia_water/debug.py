import logging
import functools

_LOGGER = logging.getLogger(__name__)

def decoratorexceptionDebug(func):
    """Decorator to catch and log exceptions in the debug log."""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _LOGGER.debug(f"Exception in {func.__name__}: {e}")
            raise

    return wrapped
