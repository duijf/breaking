import socket
from multiprocessing import Process
from typing import Iterator, Tuple

import flask
import pytest
import requests

from breaking import CircuitBreaker


@pytest.fixture
def open_port() -> int:
    """Find an open port to start a server process on."""
    sock = socket.socket()

    all_interfaces = ""
    assign_free_port = 0
    sock.bind((all_interfaces, assign_free_port))

    _, port = sock.getsockname()
    assert isinstance(port, int)

    sock.close()

    return port


@pytest.fixture
def breaker() -> CircuitBreaker:
    return CircuitBreaker(
        error_threshold=5,
        time_window_secs=1,
    )


@pytest.fixture
def not_a_server_url(open_port: int) -> str:
    return f"http://localhost:{open_port+1}"


@pytest.fixture
def server_url(open_port: int) -> str:
    return f"http://localhost:{open_port}"


@pytest.fixture(autouse=True)
def server(open_port: int) -> Iterator[None]:
    def http_root() -> Tuple[str, int]:
        return "", 500

    app = flask.Flask("tests")
    app.add_url_rule("/", "root", http_root)
    flask_proc = Process(target=app.run, kwargs={"port": open_port})
    flask_proc.start()
    yield
    flask_proc.terminate()
    flask_proc.join()


def test_successful_requests(breaker: CircuitBreaker, server_url: str) -> None:
    with breaker:
        resp = requests.get(server_url)
        assert resp.status_code == 500


def test_exception_propagation(
    breaker: CircuitBreaker, not_a_server_url: str
) -> None:
    with pytest.raises(requests.exceptions.ConnectionError):
        with breaker:
            requests.get(not_a_server_url)
