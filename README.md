# 100x

A Python client for the 100x API, providing a convenient wrapper to interact with the API.

## Installation

```shell
pip install hundred-x
````

## Usage

```python

from hundred_x.client import HundredXClient
from hundred_x.enums import Environment

client = HundredXClient(
    private_key="your_private_key",
    environment=Environment.PROD
)

# List available products
products = client.list_products()
print(products) 

# Get the current price of a symbol
price = client.get_product("ethperp")
print(price)

# Place an order
order = client.place_order(
    symbol="ethperp",
    side="BUY",
    order_type="LIMIT",
    post_only=False,
    size="0.1",
    price="1800",
    limit_fee_rate="0.001"
)
print(order)
```

For asynchronous usage, refer to 'examples/async_client.py'.

## Development

### Prequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/)

### Setup

1. Clone the repository:


```shell
git clone https://github.com/8ball030/hundred_x.git &&cd hundred_x
```

2. Create a development environment:

```shell
poetry install && poetry shell
```

### Development Commands

```shell
# Format Code
make fmt

# Lint Code
make lint

# Run Tests
make tests

# Run all checks
make all

# Create a new release
make release
```

### Docker Environemnt

```shell
# Build Docker Image
docker buildx build --platform linux/amd64 . -t test

# Run tests in Docker
docker run -v (pwd):/app -it test
```
### Contributing

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
        <a href=https://github.com/thegeronimo>
            <img src=https://avatars.githubusercontent.com/u/59147332?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=thegeronimo/>
            <br />
            <sub style="font-size:14px"><b>thegeronimo</b></sub>
        </a>
    </td>
</tr>
<tr>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/wakamex>
            <img src=https://avatars.githubusercontent.com/u/16990562?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Mihai/>
            <br />
            <sub style="font-size:14px"><b>Mihai</b></sub>
        </a>
    </td>
</tr>
</table>
