"""
Tests for the hundred.client module.
"""

from datetime import datetime
from unittest import TestCase

import pytest

from hundred_x.client import HundredXClient
from hundred_x.eip_712 import Order, Withdraw
from hundred_x.enums import Environment, OrderSide, OrderType, TimeInForce

DEFAULT_SYMBOL = "ethperp"
TEST_PRIVATE_KEY = "0x8f58e47491ac5fe6897216208fe1fed316d6ee89de6c901bfc521c2178ebe6dd"
TEST_ADDRESS = "0xEEF7faba495b4875d67E3ED8FB3a32433d3DB3b3"
TEST_ORDER = {
    "subaccount_id": 1,
    "product_id": 1002,
    "quantity": 1,
    "price": 3000,
    "side": OrderSide.BUY,
    "order_type": OrderType.LIMIT,
    "time_in_force": TimeInForce.GTC,
}

CANCEL_AND_REPLACE_ORDER = {
    "subaccount_id": 1,
    "product_id": 1002,
    "quantity": 1,
    "price": 3000,
    "side": OrderSide.BUY,
}

TEST_ORDER_DECIMAL_QUANTITY = {
    "subaccount_id": 1,
    "product_id": 1006,
    "quantity": 4000.73,
    "price": 4,
    "side": OrderSide.BUY,
    "order_type": OrderType.LIMIT,
    "time_in_force": TimeInForce.GTC,
}

TEST_ORDER_DECIMAL_PRICE = {
    "subaccount_id": 1,
    "product_id": 1002,
    "quantity": 1,
    "price": 3000.13,
    "side": OrderSide.BUY,
    "order_type": OrderType.LIMIT,
    "time_in_force": TimeInForce.GTC,
}


class Testnet(TestCase):
    """
    Base class for the Client class tests.
    """

    environment: Environment = Environment.TESTNET

    def setUp(self):
        """
        Set up the Client class tests.
        """
        self.client = HundredXClient(env=self.environment, private_key=TEST_PRIVATE_KEY, subaccount_id=1)
        cancel_order = self.client.cancel_all_orders(subaccount_id=1, product_id=1002)
        assert cancel_order is not None
        cancel_order = self.client.cancel_all_orders(subaccount_id=1, product_id=1006)
        assert cancel_order is not None

    def test_client_init(
        self,
    ):
        """
        Test the initialization of the Client class.
        """
        assert self.client is not None

    def test_list_products(
        self,
    ):
        """
        Test the get_instruments method of the Client class.
        """
        products = self.client.list_products()
        assert products is not None

    def test_get_product(
        self,
    ):
        """
        Test the get_instrument method of the Client class.
        """
        product = self.client.get_product(DEFAULT_SYMBOL)
        assert product is not None

    def test_get_server_time(
        self,
    ):
        """
        Test the get_server_time method of the Client class.
        """
        server_time = self.client.get_server_time()
        assert server_time is not None

    def test_get_candlestick(
        self,
    ):
        """
        Test the get_candlestick method of the Client class.
        """
        candlestick = self.client.get_candlestick(
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

    def test_get_symbol(
        self,
    ):
        """
        Test the get_symbol method of the Client class.
        """
        symbol = self.client.get_symbol(DEFAULT_SYMBOL)
        assert symbol["productSymbol"] == DEFAULT_SYMBOL

    def test_get_depth(
        self,
    ):
        """
        Test the get_depth method of the Client class.
        """
        depth = self.client.get_depth(DEFAULT_SYMBOL, granularity=5, limit=10)
        assert depth is not None
        assert "bids" in depth, "Failed to get depth data."
        assert "asks" in depth, "Failed to get depth data."

    def test_get_trade_history(
        self,
    ):
        """
        Test the get_trade_history method of the Client class.
        """
        trade_history = self.client.get_trade_history(DEFAULT_SYMBOL, lookback=10)
        assert trade_history is not None

    def test_login(
        self,
    ):
        """
        Test the login method of the Client class.
        """
        self.client.login()

    def test_get_session_status(
        self,
    ):
        """
        Test the get_session_status method of the Client class.
        """
        self.client.login()
        session_status = self.client.get_session_status()
        assert session_status is not None

    @pytest.mark.skip(reason="This test is not working, the session is not being destroyed")
    def test_logout(
        self,
    ):
        """
        Test the logout method of the Client class.
        """
        self.client.login()
        status = self.client.get_session_status()
        assert status["status"] == "success"

        self.client.logout()
        status = self.client.get_session_status()
        assert status["status"] != "success"

    def test_get_spot_balances(
        self,
    ):
        """
        Test the get_spot_balance method of the Client class.
        """
        self.client.login()
        balance = self.client.get_spot_balances()
        assert balance is not None

    def test_get_perpetural_position(
        self,
    ):
        """
        Test the get_perpetural_position method of the Client class.
        """
        self.client.login()
        position = self.client.get_position(DEFAULT_SYMBOL)
        assert position is not None

    def test_get_approved_signers(
        self,
    ):
        """
        Test the get_approved_signers method of the Client class.
        """
        self.client.login()
        self.client.get_approved_signers()

    def test_get_open_orders(
        self,
    ):
        """
        Test the get_open_orders method of the Client class.
        """
        self.client.login()
        orders = self.client.get_open_orders(DEFAULT_SYMBOL)
        assert orders is not None

    def test_get_orders(
        self,
    ):
        """
        Test the get_orders method of the Client class.
        https://100x.readme.io/reference/list-orders-trade
        """
        self.client.login()
        orders = self.client.get_orders()
        assert orders is not None

    def test_deposit(
        self,
    ):
        """
        Test the deposit method of the Client class.
        """
        self.client.login()
        deposit = self.client.deposit(subaccount_id=1, quantity=100)
        assert deposit is not None

    def test_withdraw(
        self,
    ):
        """
        Test the withdraw method of the Client class.
        """
        self.client.login()
        withdraw = self.client.withdraw(subaccount_id=1, quantity=100)
        assert withdraw is not None

    def test_withdraw_signature(
        self,
    ):
        """
        Test the withdraw_signature method of the Client class.
        """
        self.client._current_timestamp = lambda: 1711722371
        withdrawal_message = self.client.generate_and_sign_message(
            message_class=Withdraw,
            quantity=int(100 * 10**18),
            nonce=self.client._current_timestamp(),
            **self.client.get_shared_params(subaccount_id=1, asset="USDB"),
        )

        assert (
            withdrawal_message["signature"]
            == "0x7e943abf014646836b59d2dcf120e533f5843fc7033c95b030184c6b2b062dfe37c1bdf6b7cec4d722cc75cd6bd36eadcb91868e2cc50fd974de92ce784a47531b"  # noqa: E501
        )

    def test_order_decimal_number_quantity(
        self,
    ):
        """
        Test the order method of the Client class.
        """
        self.client.login()
        order = self.client.create_order(
            **TEST_ORDER_DECIMAL_QUANTITY,
        )
        assert order is not None

    def test_order_decimal_number_price(
        self,
    ):
        """
        Test the order method of the Client class.
        """
        self.client.login()
        order = self.client.create_order(
            **TEST_ORDER_DECIMAL_PRICE,
        )
        assert order is not None

    def test_order(
        self,
    ):
        """
        Test the order method of the Client class.
        """
        self.client.login()
        order = self.client.create_order(
            **TEST_ORDER,
        )
        assert order is not None

    def test_order_signature(self):
        """
        Test the withdraw_signature method of the Client class.
        """
        self.client._current_timestamp = lambda: 1711722373
        ts = self.client._current_timestamp()

        order_message = self.client.generate_and_sign_message(
            message_class=Order,
            expiration=(ts + 1000 * 60 * 60 * 24) * 1000,
            nonce=self.client._current_timestamp(),
            productId=TEST_ORDER["product_id"],
            isBuy=TEST_ORDER["side"].value,
            orderType=TEST_ORDER["order_type"].value,
            price=TEST_ORDER["price"] * 10**18,
            quantity=TEST_ORDER["quantity"] * 10**18,
            timeInForce=TEST_ORDER["time_in_force"].value,
            **self.client.get_shared_params(
                subaccount_id=TEST_ORDER["subaccount_id"],
                asset="USDB",
            ),
        )

        assert (
            order_message["signature"]
            == "0x4f686289d48c53017c94f554d5bc626aad44ccec5e2dc244bc7f8fe753aa40ab1151c35e88e74abca2a49ce191b03c424f89e8dfe6c34ee235ee60ad10151e7d1b"  # noqa: E501
        )

    def test_cancel_order(
        self,
    ):
        """
        Test the cancel_order method of the Client class.
        """
        self.client.login()
        order = self.client.create_order(
            **TEST_ORDER,
        )
        assert order is not None
        cancel_order = self.client.cancel_order(order['subAccountId'], order['productId'], order['id'])
        assert cancel_order is not None

    def test_cancel_orders(self):
        """
        Test the cancel_orders method of the Client class.
        """
        self.client.login()
        order = self.client.create_order(
            **TEST_ORDER,
        )
        assert order is not None
        cancel_order = self.client.cancel_all_orders(subaccount_id=1, product_id=1002)
        assert cancel_order is not None

    def test_cancel_and_replace_order(self):
        """
        Test the cancel_and_replace_order method of the Client class.
        """
        self.client.login()
        order = self.client.create_order(
            **TEST_ORDER,
        )
        assert order is not None
        cancel_order = self.client.cancel_and_replace_order(**CANCEL_AND_REPLACE_ORDER, order_id_to_cancel=order["id"])
        assert cancel_order is not None

    def test_set_referral_code(self):
        """
        Test the set_referral_code method of the Client class.
        """
        self.client.login()
