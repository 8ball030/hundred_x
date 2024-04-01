"""
Tests for the hundred.client module.
"""

from datetime import datetime

import pytest

from hundred_x.client import HundredXClient
from hundred_x.enums import Environment, OrderSide, OrderType, TimeInForce

DEFAULT_SYMBOL = "ethperp"
TEST_PRIVATE_KEY = "0x8f58e47491ac5fe6897216208fe1fed316d6ee89de6c901bfc521c2178ebe6dd"
TEST_ADDRESS = "0xEEF7faba495b4875d67E3ED8FB3a32433d3DB3b3"


@pytest.fixture
def client():
    """
    Fixture for the Client class.
    """
    return HundredXClient(env=Environment.TESTNET, private_key=TEST_PRIVATE_KEY)


def test_client_init(client):
    """
    Test the initialization of the Client class.
    """
    assert client is not None


def test_list_products(client):
    """
    Test the get_instruments method of the Client class.
    """
    products = client.list_products()
    assert products is not None


def test_get_product(client):
    """
    Test the get_instrument method of the Client class.
    """
    product = client.get_product(DEFAULT_SYMBOL)
    assert product is not None


def test_get_server_time(client):
    """
    Test the get_server_time method of the Client class.
    """
    server_time = client.get_server_time()
    assert server_time is not None


def test_get_candlestick(client):
    """
    Test the get_candlestick method of the Client class.
    """
    candlestick = client.get_candlestick(
        symbol=DEFAULT_SYMBOL,
        interval="1m",
        start_time=int(datetime.now().timestamp() - 3600) * 1000,
        end_time=int(
            datetime.now().timestamp(),
        )
        * 1000,
        limit=100,
    )
    assert isinstance(candlestick, list), f"Failed to get candlestick data. {candlestick}"
    assert len(candlestick) > 0, f"Failed to get candlestick data. {candlestick}"


def test_get_symbol(client):
    """
    Test the get_symbol method of the Client class.
    """
    symbol = client.get_symbol(DEFAULT_SYMBOL)
    assert symbol["productSymbol"] == DEFAULT_SYMBOL


def test_get_depth(client):
    """
    Test the get_depth method of the Client class.
    """
    depth = client.get_depth(DEFAULT_SYMBOL, granularity=5, limit=10)
    assert depth is not None
    assert "bids" in depth, "Failed to get depth data."
    assert "asks" in depth, "Failed to get depth data."


def test_login(client):
    """
    Test the login method of the Client class.
    """
    client.login()


def test_get_session_status(client):
    """
    Test the get_session_status method of the Client class.
    """
    client.login()
    session_status = client.get_session_status()
    assert session_status is not None


@pytest.mark.skip(reason="This test is not working, the session is not being destroyed")
def test_logout(client):
    """
    Test the logout method of the Client class.
    """
    client.login()
    status = client.get_session_status()
    assert status["status"] == "success"

    client.logout()
    status = client.get_session_status()
    assert status["status"] != "success"


def test_get_spot_balances(client):
    """
    Test the get_spot_balance method of the Client class.
    """
    client.login()
    balance = client.get_spot_balances()
    assert balance is not None


def test_get_perpetural_position(client):
    """
    Test the get_perpetural_position method of the Client class.
    """
    client.login()
    position = client.get_position(DEFAULT_SYMBOL)
    assert position is not None


def test_get_approved_signers(client):
    """
    Test the get_approved_signers method of the Client class.
    """
    client.login()
    client.get_approved_signers()


def test_get_open_orders(client):
    """
    Test the get_open_orders method of the Client class.
    """
    client.login()
    orders = client.get_open_orders(DEFAULT_SYMBOL)
    assert orders is not None


# @pytest.mark.skip(
#     reason="This test is not working, the endpoint fails with incorrect parameters"
# )
def test_get_orders(client):
    """
    Test the get_orders method of the Client class.
    https://100x.readme.io/reference/list-orders-trade
    """
    client.login()
    orders = client.get_orders()
    assert orders is not None


def test_deposit(client):
    """
    Test the deposit method of the Client class.
    """
    client.login()
    deposit = client.deposit(subaccount_id=0, quantity=100)
    assert deposit is not None


def test_withdraw(client):
    """
    Test the withdraw method of the Client class.
    """
    client.login()
    withdraw = client.withdraw(subaccount_id=0, quantity=100)
    assert withdraw is not None


def test_withdraw_signature(client):
    """
    Test the withdraw_signature method of the Client class.
    """
    client._current_timestamp = lambda: 1711722371
    withdrawal_message = client.generate_withdrawal_message(subaccount_id=0, quantity=100)

    assert (
        withdrawal_message["signature"]
        == "0x334a617170bd712c183ac1765bd207da6a029d9203eb5cda87fa3900b98713f86dc63d53318200ce9d889021743d84df6d41d352d452ec9370f1ef4f1a2a01141b"  # noqa: E501
    )


def test_order(client):
    """
    Test the order method of the Client class.
    """
    client.login()
    order = client.create_order(
        subaccount_id=0,
        product_id=1002,
        quantity=1,
        price=3000,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
    )
    assert order is not None


def test_order_signature(client):
    """
    Test the withdraw_signature method of the Client class.
    """
    client._current_timestamp = lambda: 1711722373
    order_message = client.generate_order_message(
        subaccount_id=0,
        product_id=1002,
        quantity=1,
        price=3000,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
    )

    assert (
        order_message["signature"]
        == "0x54ab1e8df6f6551aece55038c1c355b6a510163c01c2bb6fa828fc26696725364a00636e3a858cd8197e5451bdbce43b0c7e47770cce103680e4948f26449a311b"  # noqa: E501
    )


def test_cancel_order(client):
    """
    Test the cancel_order method of the Client class.
    """
    client.login()
    order = client.create_order(
        subaccount_id=0,
        product_id=1002,
        quantity=1,
        price=3000,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
    )
    assert order is not None
    cancel_order = client.cancel_order(subaccount_id=0, product_id=1002, order_id=order["id"])
    assert cancel_order is not None


def test_cancel_orders(client):
    """
    Test the cancel_orders method of the Client class.
    """
    client.login()
    order = client.create_order(
        subaccount_id=0,
        product_id=1002,
        quantity=1,
        price=3000,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
    )
    assert order is not None
    cancel_order = client.cancel_all_orders(subaccount_id=0, product_id=1002)
    assert cancel_order is not None


@pytest.mark.skip(reason="This test is not working, the endpoint fails with 400 response.")
def test_cancel_and_replace_order(client):
    """
    Test the cancel_and_replace_order method of the Client class.
    """
    client.login()
    order = client.create_order(
        subaccount_id=0,
        product_id=1002,
        quantity=1,
        price=3000,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
    )
    assert order is not None
    cancel_order = client.cancel_and_replace_order(
        subaccount_id=0,
        product_id=1002,
        quantity=2,
        price=4000,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
        order_id_to_cancel=order["id"],
    )
    assert cancel_order is not None
