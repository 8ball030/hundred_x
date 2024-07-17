"""
Tests for the hundred.client module.
"""

from datetime import datetime
from unittest import TestCase

import pytest

from hundred_x.client import HundredXClient
from hundred_x.eip_712 import Order, Withdraw
from hundred_x.enums import Environment
from tests.test_data import (
    CANCEL_AND_REPLACE_ORDER,
    DEFAULT_SYMBOL,
    TEST_ORDER,
    TEST_ORDER_DECIMAL_PRICE,
    TEST_ORDER_DECIMAL_QUANTITY,
    TEST_PRIVATE_KEY,
)


class Client:
    """
    Base class for the Client class tests.
    """

    environment: Environment = Environment.DEVNET

    def setUp(self):
        """
        Set up the Client class tests.
        """
        self.client = HundredXClient(env=self.environment, private_key=TEST_PRIVATE_KEY, subaccount_id=1)

    def tearDown(self):
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
        position = self.client.get_position()
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
        signature="0x7e943abf014646836b59d2dcf120e533f5843fc7033c95b030184c6b2b062dfe37c1bdf6b7cec4d722cc75cd6bd36eadcb91868e2cc50fd974de92ce784a47531b",  # noqa: E501
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

        assert withdrawal_message["signature"] == signature

    @pytest.mark.skip(reason="This test is not working to due none implementaiton of rounding.")
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

    @pytest.mark.skip(reason="This test is not working to due none implementaiton of rounding.")
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

    def test_order_signature(
        self,
        signature="0x4f686289d48c53017c94f554d5bc626aad44ccec5e2dc244bc7f8fe753aa40ab1151c35e88e74abca2a49ce191b03c424f89e8dfe6c34ee235ee60ad10151e7d1b",  # noqa: E501
    ):
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

        assert order_message["signature"] == signature

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
        cancel_order = self.client.cancel_order(order['productId'], order['id'], order['subAccountId'])
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


@pytest.mark.dev
class TestDevClient(Client, TestCase):
    """
    Base class for the Client class tests.
    """

    environment: Environment = Environment.DEVNET


class TestStagingClient(Client, TestCase):
    """
    Base class for the Client class tests.
    """

    environment: Environment = Environment.TESTNET

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_deposit(
        self,
    ):
        super().test_deposit()

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_withdraw(self):
        return super().test_withdraw()

    def test_withdraw_signature(self):
        signature = '0x716869414978aae79b4dbed32d27c68002ed9070967c2026466e7af5c07b4f5a24ee2b333201f48b2257766aca45b99f31709b778acce5e71747d7a1be3026121b'  # noqa: E501
        return super().test_withdraw_signature(signature=signature)

    def test_order_signature(self):
        return super().test_order_signature(
            signature="0xb7f6141dad52ff2a26c5834313dc07fac85ee66ce44997204c4df995447523e254f60b1eb0b7537158b4f23d5e648cffed503c29e05b972d4c100ce6680d4b611c"  # noqa: E501
        )


class TestProdClient(Client, TestCase):
    """
    Base class for the Client class tests.
    """

    environment: Environment = Environment.PROD

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_deposit(
        self,
    ):
        super().test_deposit()

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_withdraw(self):
        return super().test_withdraw()

    def test_withdraw_signature(self):
        signature = '0x04a512b60f41f4429d030f1dea3d29544e28fad573582e033d55da25ef6c2e8153ca256637088369de25dbcbb8f2bde7e2fe3fb193240c3f3fd90169858999f81c'  # noqa: E501
        return super().test_withdraw_signature(signature=signature)

    def test_order_signature(self):
        return super().test_order_signature(
            signature="0x38c34757dd73104595871b471143d4ce0d95eec7d020e4950830921cb0eec0427ef284dfc6fc5c65b2319179a73d16f84f5d6a1d2e0d1a301caa665112d440601c"  # noqa: E501
        )

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_cancel_order(
        self,
    ):
        return super().test_cancel_order()

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_cancel_orders(self):
        return super().test_cancel_orders()

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_cancel_and_replace_order(self):
        return super().test_cancel_and_replace_order()

    @pytest.mark.skip(reason="This test is not working to due insufficient balances")
    def test_order(
        self,
    ):
        return super().test_order()
