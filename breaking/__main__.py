#!/usr/bin/env python
import time

import requests

from breaking import CircuitBreaker, RequestBlockedError

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

# Perform a request which should raise the RequestBlockedError.
# This is printed on stdout.
try:
    breaker.request("GET", failing_url)
except RequestBlockedError as e:
    print(e)

# Wait until the error_threshold has lifted
print("Waiting until we can perform requests again")
time.sleep(time_window_secs)

# Perform a few requests again (it fails again)
try:
    breaker.request("GET", failing_url)
except requests.exceptions.ConnectionError:
    print("Request failed again")
