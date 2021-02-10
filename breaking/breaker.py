from types import TracebackType
from typing import Optional, Tuple, Type

from breaking.bucket import TokenBucket
from breaking.clock import Clock, MonotonicClock


class TooManyErrors(Exception):
    """
    Raised by `CircuitBreaker` when too many errors have occurred.
    """


class CircuitBreaker:
    """
    Stop executing code after too many exceptions have been occurred.

    Allows a maximum number of `error_threshold` errors over a time window of
    `time_window_secs`. After this threshold has been exceeded, we disallow any
    further requests until enough time has passed.

    See `breaking.bucket.TokenBucket` for further details on how requests are
    replenished.

    If `exceptions_types` is passed, the CircuitBreaker will only count
    exceptions of the given types. All these exceptions are re-raised.

    This class is a ContextManager, so you can use it in a `with` statement.
    """

    def __init__(
        self,
        error_threshold: int,
        time_window_secs: int,
        exceptions_types: Tuple[Type[Exception], ...] = (Exception,),
        clock: Optional[Clock] = None,
    ):
        self._exception_types = exceptions_types

        restore_rate_hz = error_threshold / time_window_secs

        if clock is None:
            clock = MonotonicClock()

        self._bucket = TokenBucket(
            capacity_max=error_threshold,
            restore_rate_hz=restore_rate_hz,
            clock=clock,
        )

    def __enter__(self) -> None:
        print("Asked to perform request.")
        if self.is_blocking_execution():
            raise TooManyErrors("Not performing request. Too many failures")

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None:
        """Exit the context manager.

        If this method returns `True`, the runtime will ignore any raised
        exceptions in the body of the contextmanager. We don't use this
        feature, so this method returns `None`.
        """
        if exc_type is None:
            return

        # Check whether the raised exception is part of the configured
        # exceptions that the user wants to count. If so, record an extra
        # failure.
        for kind in self._exception_types:
            if issubclass(exc_type, kind):
                self.record_failure()

    def is_allowing_execution(self) -> bool:
        """
        Check if the circuit breaker is allowing execution.
        """
        return self._bucket.has_tokens_left()

    def is_blocking_execution(self) -> bool:
        """
        Check if the circuit breaker is blocking execution.
        """
        return not self.is_allowing_execution()

    def record_failure(self) -> None:
        """
        Record a failed call in the state of this circuit breaker.
        """
        self._bucket.take()
