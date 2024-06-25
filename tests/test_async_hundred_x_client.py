import pytest
import respx
from httpx import Response
from decimal import Decimal
from hundred_x.enums import OrderSide, OrderType, TimeInForce
from hundred_x.async_client import AsyncHundredXClient
from hundred_x.enums import Environment

TEST_PRIVATE_KEY = "0x8f58e47491ac5fe6897216208fe1fed316d6ee89de6c901bfc521c2178ebe6dd"

@pytest.fixture
def client():
    env = Environment.PROD
    return AsyncHundredXClient(env, TEST_PRIVATE_KEY)

BASE_URL = "https://api.100x.finance"

@pytest.mark.asyncio
@respx.mock
async def test_get_symbol_info(client):
    symbol = "BTCUSD"
    respx.get(f"{BASE_URL}/v1/ticker/24hr", params={"symbol": symbol}).mock(
        return_value=Response(200, json=[{"symbol": symbol, "price": "50000.00"}])
    )
    response = await client.get_symbol_info(symbol)
    assert response["symbol"] == symbol
    assert response["price"] == "50000.00"

@pytest.mark.asyncio
@respx.mock
async def test_get_depth(client):
    symbol = "BTCUSD"
    respx.get(f"{BASE_URL}/v1/depth", params={"symbol": symbol, "limit": 5}).mock(
        return_value=Response(200, json={"bids": [], "asks": []})
    )
    response = await client.get_depth(symbol)
    assert "bids" in response
    assert "asks" in response

@pytest.mark.asyncio
@respx.mock
async def test_get_trade_history(client):
    symbol = "BTCUSD"
    lookback = 10
    respx.get(f"{BASE_URL}/v1/trade-history", params={"symbol": symbol, "limit": lookback}).mock(
        return_value=Response(200, json=[{"id": 1, "price": "50000.00"}])
    )
    response = await client.get_trade_history(symbol, lookback)
    assert isinstance(response, list)
    assert response[0]["id"] == 1
    assert response[0]["price"] == "50000.00"

@pytest.mark.asyncio
@respx.mock
async def test_create_and_send_order(client):
    subaccount_id = 1
    product_id = 1
    quantity = 1
    price = 50000
    side = OrderSide.BUY
    order_type = OrderType.LIMIT
    time_in_force = TimeInForce.GTC
    respx.post(f"{BASE_URL}/v1/order").mock(
        return_value=Response(200, json={"orderId": "12345"})
    )
    response = await client.create_and_send_order(
        subaccount_id, product_id, quantity, price, side, order_type, time_in_force
    )
    assert response["orderId"] == "12345"

@pytest.mark.asyncio
@respx.mock
async def test_cancel_order(client):
    product_id = 1
    order_id = "12345"  # Changing order_id to string
    respx.delete(f"{BASE_URL}/v1/order").mock(
        return_value=Response(200, json={"status": "success"})
    )
    response = await client.cancel_order(product_id, order_id)
    assert response["status"] == "success"

@pytest.mark.asyncio
@respx.mock
async def test_get_open_orders(client):
    symbol = "BTCUSD"
    respx.get(f"{BASE_URL}/v1/openOrders", params={"symbol": symbol, "account": client.public_key, "subAccountId": client.subaccount_id}).mock(
        return_value=Response(200, json=[{"orderId": "12345", "symbol": symbol}])
    )
    response = await client.get_open_orders(symbol)
    assert isinstance(response, list)
    assert response[0]["orderId"] == "12345"
    assert response[0]["symbol"] == symbol