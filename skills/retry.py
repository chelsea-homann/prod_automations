"""
Skill 6.4 - Network retry with exponential backoff
===================================================
Wrap flaky network operations (report pulls, SFTP, SMTP) so transient blips
don't fail an otherwise-healthy run. Only transient/connection errors are
retried; authentication and 4xx client errors fail fast.

Usage
-----
    from skills.retry import retry, with_retry

    @retry(max_attempts=4, base_delay=2.0)
    def pull():
        ...

    # or wrap a call inline
    result = with_retry(lambda: pull(), max_attempts=4)
"""

import time
import functools

# Exceptions that are worth retrying. requests/paramiko raise subclasses of these.
TRANSIENT_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,  # covers socket.error, paramiko SSHException-style failures
)


def _is_retryable(exc):
    """Return True for transient errors, False for auth/4xx client errors."""
    # requests HTTPError carries a response; never retry 4xx (client) errors.
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    if status is not None and 400 <= status < 500:
        return False
    if isinstance(exc, TRANSIENT_EXCEPTIONS):
        return True
    # requests.exceptions.RequestException isn't an OSError subclass; match by name.
    return exc.__class__.__name__ in {
        "ConnectionError", "Timeout", "ConnectTimeout", "ReadTimeout",
        "ChunkedEncodingError", "SSHException",
    }


def retry(max_attempts=4, base_delay=2.0, backoff=2.0, exceptions=None):
    """
    Decorator: retry the wrapped function with exponential backoff.

    Delays follow base_delay * backoff**n -> 2s, 4s, 8s, 16s by default.

    Parameters
    ----------
    max_attempts : int   Total attempts before giving up (default 4).
    base_delay : float   Seconds before the first retry (default 2.0).
    backoff : float      Multiplier applied to the delay each attempt (default 2.0).
    exceptions : tuple   Override the default transient-exception detection.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001 - re-raised below if not retryable
                    attempt += 1
                    retryable = (
                        isinstance(exc, exceptions) if exceptions else _is_retryable(exc)
                    )
                    if not retryable or attempt >= max_attempts:
                        raise
                    delay = base_delay * (backoff ** (attempt - 1))
                    print(f"  [retry] {func.__name__} failed ({exc}); "
                          f"attempt {attempt}/{max_attempts - 1}, waiting {delay:.0f}s")
                    time.sleep(delay)
        return wrapper
    return decorator


def with_retry(func, *args, max_attempts=4, base_delay=2.0, backoff=2.0,
               exceptions=None, **kwargs):
    """Call ``func(*args, **kwargs)`` with the same retry policy as ``@retry``."""
    wrapped = retry(max_attempts=max_attempts, base_delay=base_delay,
                    backoff=backoff, exceptions=exceptions)(func)
    return wrapped(*args, **kwargs)
