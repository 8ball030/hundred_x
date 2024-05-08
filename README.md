# 100x Python Client

This is a Python client for the 100x API. It is a simple wrapper around the API, and provides a convenient way to interact with the API from Python.

## Installation
```bash
pip install hundred-x
``

## Running a dockerised environment
```bash
docker buildx build --platform linux/amd64 . -t test
# now we have the dependencies installed,
# we can mount the current directory and run the tests against the dockerised environment
docker run -v (pwd):/app -it test
```