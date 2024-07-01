"""
Tests for the async client.
"""

import pytest
import respx
from httpx import Response

from hundred_x.async_client import AsyncHundredXClient
from hundred_x.enums import Environment
from tests.test_data import TEST_ORDER_ID, TEST_PRICE, TEST_PRIVATE_KEY, TEST_SYMBOL


@pytest.fixture
def client():
    env = Environment.PROD
    return AsyncHundredXClient(env, TEST_PRIVATE_KEY)


@pytest.mark.asyncio
@respx.mock
async def test_get_symbol(
    client,
):
    respx.get(f"{client.rest_url}/v1/ticker/24hr", params={"symbol": TEST_SYMBOL}).mock(
        return_value=Response(200, json=[{"productSymbol": TEST_SYMBOL}])
    )
    response = await client.get_symbol(TEST_SYMBOL)
    assert response["productSymbol"] == TEST_SYMBOL


@pytest.mark.asyncio
async def test_get_depth(client):
    respx.get(f"{client.rest_url}/v1/depth", params={"symbol": TEST_SYMBOL, "limit": 5}).mock(
        return_value=Response(200, json={"bids": [], "asks": []})
    )
    response = await client.get_depth(TEST_SYMBOL)
    assert "bids" in response
    assert "asks" in response


@pytest.mark.asyncio
@respx.mock
async def test_get_trade_history(client):
    respx.get(
        f"{client.rest_url}/v1/trade-history",
        params={"symbol": TEST_SYMBOL},
    ).mock(return_value=Response(200, json={"success": True, "trades": [{"id": TEST_ORDER_ID, "price": TEST_PRICE}]}))
    response = await client.get_trade_history(TEST_SYMBOL)
    assert isinstance(response['trades'], list)
    assert response['trades'][0]["id"] == TEST_ORDER_ID
    assert response['trades'][0]["price"] == TEST_PRICE


@pytest.mark.asyncio
@respx.mock
async def test_get_position(client):
    respx.get(
        f"{client.rest_url}/v1/positionRisk",
    ).mock(return_value=Response(200, json={"symbol": TEST_SYMBOL}))
    response = await client.get_position(TEST_SYMBOL)
    assert response["symbol"] == TEST_SYMBOL


@pytest.mark.asyncio
@respx.mock
async def test_get_spot_balances(client):
    respx.get(
        f"{client.rest_url}/v1/balances", params={"account": client.public_key, "subAccountId": client.subaccount_id}
    ).mock(return_value=Response(200, json={"balances": []}))
    response = await client.get_spot_balances()
    assert "balances" in response


@pytest.mark.asyncio
@respx.mock
async def test_get_open_orders(client):
    respx.get(f"{client.rest_url}/v1/openOrders", params={"symbol": TEST_SYMBOL}).mock(
        return_value=Response(200, json=[{"orderId": "12345", "symbol": TEST_SYMBOL}])
    )
    response = await client.get_open_orders(TEST_SYMBOL)
    assert isinstance(response, list)
    assert response[0]["orderId"] == "12345"
    assert response[0]["symbol"] == TEST_SYMBOL


@pytest.mark.asyncio
@respx.mock
async def test_cancel_order(client):
    respx.delete(
        f"{client.rest_url}/v1/order",
    ).mock(return_value=Response(200, json={"orderId": TEST_ORDER_ID}))
    response = await client.cancel_order(order_id=TEST_ORDER_ID, product_id=1002)
    assert response["orderId"] == TEST_ORDER_ID
