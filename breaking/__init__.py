#!/usr/bin/env python
import enum
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import requests


class State(enum.Enum):
    """
    States for the circuit breaker.
    """

    ALLOWS_REQUESTS = enum.auto()
    BLOCKS_REQUESTS = enum.auto()


class CircuitOpenError(Exception):
    """
    Exception raised by `CircuitBreaker` when asked to preform a
    request with an open circuit.
    """


class CircuitBreaker:
    """
    A toy circuit breaker in Python for HTTP requests.

    Will use `http_client.request()` to perform requests. This method
    assumes the API contract of the `requests` library. This could be
    a little more library agnostic, but this wasn't clear from the
    requirements.

    Stops allowing requests after `error_threshold` number of errors
    have happened. (NB: This does not consider the `time_window_secs`
    parameter like you'd probably expect.)

    Starts allowing requests after `time_window_secs` since the last
    error again.
    """

    # NB: It would be nice to design a mypy `Protocol` for the `http_client`
    # parameter so we could benefit from type checking. Didn't have time for
    # that though.
    def __init__(
        self, http_client: Any, error_threshold: int, time_window_secs: int
    ):
        self._http_client = http_client
        self._error_threshold = error_threshold
        self._time_window = timedelta(seconds=time_window_secs)

        # Set the last error to the UNIX epoch. This allows us to avoid
        # a nullable variable.
        self._last_error = datetime.fromtimestamp(0, tz=timezone.utc)
        self._state = State.ALLOWS_REQUESTS
        self._error_count_since_last_close = 0

    def request(self, method, url):
        """
        Make a HTTP request to `url` using `method`.
        """
        print("Asked to perform request.")

        if self.is_blocking_requests():
            raise CircuitOpenError(
                "Circuit open. Did not perform request. Too many failures"
            )

        print("Circuit closed. Performing request")

        try:
            response = self._http_client.request(method, url)
            return response

        # In a production implementation, catching all kinds of exceptions
        # is bad form. This should probably be configurable.
        except Exception:
            # Record that the call failed and reraise the exception.
            self.record_failure()
            raise

    def is_blocking_requests(self) -> bool:
        """
        Check if the circuit breaker is blocking requests.
        """
        # Set the state back to closed if the last error was outside of the
        # time window we care about. Also reset some of the meta variables.
        if self._last_error <= (
            datetime.now(timezone.utc) - self._time_window
        ):
            print(
                f"Last error happened at {self._last_error}. Resetting state."
            )
            self._state = State.ALLOWS_REQUESTS
            self._error_count_since_last_close = 0

        return self._state == State.BLOCKS_REQUESTS

    def record_failure(self) -> None:
        """
        Record a failed call in the state of this circuit breaker.
        """
        self._last_error = datetime.now(timezone.utc)
        self._error_count_since_last_close += 1

        if self._error_count_since_last_close >= self._error_threshold:
            print("Circuit breaker triggered.")
            self._state = State.BLOCKS_REQUESTS


def main() -> None:
    failing_url = "http://localhost:5000"
    time_window_secs = 5

    breaker = CircuitBreaker(
        http_client=requests,
        error_threshold=5,
        time_window_secs=time_window_secs,
    )

    # Perform 5 failing requests.
    for _ in range(5):
        try:
            breaker.request("GET", failing_url)
        except requests.exceptions.ConnectionError:
            print("Request failed")

    # Perform a request which should raise the CircuitOpenError.
    # This is printed on stdout.
    try:
        breaker.request("GET", failing_url)
    except CircuitOpenError as e:
        print(e)

    # Wait until the error_threshold has lifted
    print("Waiting until we can perform requests again")
    time.sleep(time_window_secs)

    # Perform a few requests again (it fails again)
    try:
        breaker.request("GET", failing_url)
    except requests.exceptions.ConnectionError:
        print("Request failed again")
