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

<table>
<tr>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/8ball030>
            <img src=https://avatars.githubusercontent.com/u/35799987?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=8ball030/>
            <br />
            <sub style="font-size:14px"><b>8ball030</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/kjr217>
            <img src=https://avatars.githubusercontent.com/u/55159119?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=kjr217/>
            <br />
            <sub style="font-size:14px"><b>kjr217</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/wakamex>
            <img src=https://avatars.githubusercontent.com/u/16990562?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Mihai/>
            <br />
            <sub style="font-size:14px"><b>Mihai</b></sub>
        </a>
    </td>
</tr>
</table>

