# Breaking

A toy circuit breaker implementation in Python. Please consult
`./breaking.py` for details.

## Setup

```
# Set up a virtualenv and install requests.
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# Now run the demo program.
$ ./breaking.py
```

## Future work

Things that would be nice to include:

 - A test suite instead of the little exectuable proof of concept.
 - Typesafe support for other HTTP clients with mypy protocols.

## Context

In case you're following me on GitHub and are wondering what's
happening: I'm writing this as part of the interview process for a
company I'm interviewing at.
