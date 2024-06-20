# 100x Python Client

This is a Python client for the 100x API. It is a simple wrapper around the API, and provides a convenient way to interact with the API from Python.

The client offers a number of methods to interact with the API.

## Usage

```python

from hundred_x.client import HundredXClient
from hundred_x.enums import Environment

DEFAULT_SYMBOL="ethperp"

client = HundredXClient(
    private_key="your_private_key",
    environment=Environment.PROD
)

# Get the current price of a symbol
products = client.list_products()
print(products) 

# Get the current price of a symbol
price = client.get_product(DEFAULT_SYMBOL)
print(price)
```



## Installation
```bash
pip install hundred-x
```

## Running a dockerised environment
```bash
docker buildx build --platform linux/amd64 . -t test
# now we have the dependencies installed,
# we can mount the current directory and run the tests against the dockerised environment
docker run -v (pwd):/app -it test
```


## Development

### Installation

```bash
git clone git@github.com:8ball030/hundred_x.git
cd hundred_x
make install
```

### Formatting

```bash
make fmt
```

### Linting

```bash
make lint
```

### Tests

```bash
make tests
```

For convience, all commands can be run with:

```
make all
```

## Releasing

Release
```bash
make release
```


### Contributors

