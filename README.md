# Breaking

A circuit breaker implementation in Python.

 - [**Docs**](https://breaking.duijf.io/breaking)

## Development

The most convenient way to set up a development environment is to use
[the Nix package manager](https://nixos.org/). After installing Nix,
you can use the `./bin/dev-shell.sh` script to get a shell which

The Nix environment is a convenience, not a requirement. You are free
to configure your development environment how you see fit. Refer to
`shell.nix` for a list of dependencies.

```
$ git clone git@github.com:duijf/breaking.git
$ cd breaking

# Set up a development shell with Nix. This get's you the right
# version of python, plus any development and test dependencies.
# These versions will not interfere with your globally installed
# tools. See `shell.nix` for what's included.
$ ./bin/dev-shell.sh

# Run the test-suite.
$ ./bin/test.sh

# Run the pre-commit checks.
$ ./bin/pre-commit.py

# Install the pre-commit checks as a git hook. After you run this
# command, you will only be able to create git commits in the breaking
# repo from a dev shell.
$ ./bin/pre-commit.py --install
```

## Why?

I wrote this code for educational + self-promotion reasons:

 - I wanted to show off my preferred way of writing Python, including
   best practices I follow. (The first version of this code was written
   for an assessment I did as part of an interview process).
 - This should also serve as an example of using the Nix package
   manager for Python development.
