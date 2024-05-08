"""

Client class is a wrapper around the REST API of the exchange. It provides methods to interact with the exchange API.
"""

from decimal import Decimal
import time
from typing import Any, List

import eth_account
import requests
from eip712_structs import make_domain
from eth_account.messages import encode_structured_data
from web3 import Web3
from web3.exceptions import TransactionNotFound

from hundred_x.constants import APIS, CONTRACTS, LOGIN_MESSAGE
from hundred_x.eip_712 import CancelOrder, CancelOrders, LoginMessage, Order, Withdraw
from hundred_x.enums import ApiType, Environment, OrderSide, OrderType, TimeInForce
from hundred_x.utils import from_message_to_payload, get_abi

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


PROTOCOL_ABI = get_abi("protocol")
ERC_20_ABI = get_abi("erc20")


class HundredXClient:
    def __init__(
        self,
        env: Environment = Environment.TESTNET,
        private_key: str = None,
        subaccount_id: int = 0,
    ):
        """
        Initialize the client with the given environment.
        """
        self.env = env
        self.rest_url = APIS[env][ApiType.REST]
        self.websocket_url = APIS[env][ApiType.WEBSOCKET]
        self.wallet = eth_account.Account.from_key(private_key)
        self.public_key = self.wallet.address
        self.subaccount_id = subaccount_id
        self.session_cookie = {}
        self.web3 = Web3(Web3.HTTPProvider("https://sepolia.blast.io"))
        self.domain = make_domain(
            name="100x",
            version="0.0.0",
            chainId=CONTRACTS[env]["CHAIN_ID"],
            verifyingContract=CONTRACTS[env]["VERIFYING_CONTRACT"],
        )

    def _current_timestamp(self):
        timestamp_ms = int(time.time() * 1000)
        return timestamp_ms

    def generate_and_sign_message(self, message_class, **kwargs):
        """
        Generate and sign a message.
        """
        message = message_class(**kwargs)
        message = message.to_message(self.domain)
        signable_message = encode_structured_data(message)
        signed = self.wallet.sign_message(signable_message)
        message["message"]["signature"] = signed.signature.hex()
        return message["message"]

    def get_shared_params(self, asset: str = None, subaccount_id: int = None):
        params = {
            "account": self.public_key,
        }
        if asset is not None:
            params["asset"] = self.get_contract_address(asset)
        if subaccount_id is not None:
            params["subAccountId"] = subaccount_id
        return params

    def send_message_to_endpoint(self, endpoint: str, method: str, message: dict, authenticated: bool = True):
        """
        Send a message to an endpoint.
        """
        payload = from_message_to_payload(message)
        response = requests.request(
            method,
            self.rest_url + endpoint,
            headers={} if not authenticated else self.authenticated_headers,
            json=payload,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text} {response.status_code} {self.rest_url} {payload}")
        return response.json()

    def withdraw(self, subaccount_id: int, quantity: int, asset: str = "USDB"):
        """
        Generate a withdrawal message and sign it.
        """

        message = self.generate_and_sign_message(
            Withdraw,
            quantity=int(quantity * 1e18),
            nonce=self._current_timestamp(),
            **self.get_shared_params(subaccount_id=subaccount_id, asset=asset),
        )
        return self.send_message_to_endpoint("/v1/withdraw", "POST", message)

    def create_order(
        self,
        subaccount_id: int,
        product_id: int,
        quantity: int,
        price: int,
        side: OrderSide,
        order_type: OrderType,
        time_in_force: TimeInForce,
        nonce: int = 0,
    ):
        """
        Create an order.
        """
        ts = self._current_timestamp()
        if nonce == 0:
            nonce = ts
        message = self.generate_and_sign_message(
            Order,
            subAccountId=subaccount_id,
            productId=product_id,
            quantity=int(Decimal(str(quantity)) * Decimal(1e18)),
            price=int(Decimal(str(price)) * Decimal(1e18)),
            isBuy=side.value,
            orderType=order_type.value,
            timeInForce=time_in_force.value,
            nonce=nonce,
            expiration=(ts + 1000 * 60 * 60 * 24) * 1000,
            **self.get_shared_params(),
        )
        return self.send_message_to_endpoint("/v1/order", "POST", message)

    def cancel_and_replace_order(
        self,
        subaccount_id: int,
        product_id: int,
        quantity: int,
        price: int,
        side: OrderSide,
        order_type: OrderType,
        time_in_force: TimeInForce,
        order_id_to_cancel: str,
    ):
        """
        Cancel and replace an order.
        """
        ts = self._current_timestamp()
        message = self.generate_and_sign_message(
            Order,
            subAccountId=subaccount_id,
            productId=product_id,
            quantity=int(Decimal(str(quantity)) * Decimal(1e18)),
            price=int(Decimal(str(price)) * Decimal(1e18)),
            isBuy=side.value,
            orderType=order_type.value,
            timeInForce=time_in_force.value,
            nonce=ts,
            expiration=(ts + 1000 * 60 * 60 * 24) * 1000,
            **self.get_shared_params(),
        )
        message["orderIdToCancel"] = order_id_to_cancel
        return self.send_message_to_endpoint("/v1/cancel-and-replace", "PUT", message)

    def cancel_order(self, subaccount_id: int, product_id: int, order_id: int):
        """
        Cancel an order.
        """
        message = self.generate_and_sign_message(
            CancelOrder,
            subAccountId=subaccount_id,
            productId=product_id,
            orderId=order_id,
            **self.get_shared_params(),
        )
        return self.send_message_to_endpoint("/v1/order", "DELETE", message)

    def cancel_all_orders(self, subaccount_id: int, product_id: int):
        """
        Cancel all orders.
        """
        message = self.generate_and_sign_message(
            CancelOrders,
            subAccountId=subaccount_id,
            productId=product_id,
            **self.get_shared_params(),
        )
        return self.send_message_to_endpoint("/v1/openOrders", "DELETE", message)

    def create_authenticated_session_with_service(self):
        login_payload = self.generate_and_sign_message(
            LoginMessage,
            message=LOGIN_MESSAGE,
            timestamp=self._current_timestamp(),
            **self.get_shared_params(),
        )
        response = self.send_message_to_endpoint("/v1/session/login", "POST", login_payload, authenticated=False)
        self.session_cookie = response.get("value")
        return response

    def list_products(self) -> List[Any]:
        """
        Get a list of all available products.
        """
        return requests.get(self.rest_url + "/v1/products").json()

    def get_product(self, product_symbol: str) -> Any:
        """
        Get the details of a specific product.
        """
        return requests.get(self.rest_url + f"/v1/products/{product_symbol}").json()

    def get_trade_history(self, symbol: str, lookback: int) -> Any:
        """
        Get the trade history for a specific product symbol and lookback amount.
        """
        return requests.get(
            self.rest_url + "/v1/trade-history",
            params={"symbol": symbol, "lookback": lookback},
        ).json()

    def get_server_time(self) -> Any:
        """
        Get the server time.
        """
        return requests.get(self.rest_url + "/v1/time").json()

    def get_candlestick(self, symbol: str, **kwargs) -> Any:
        """
        Get the candlestick data for a specific product.
        """
        params = {"symbol": symbol}
        for arg in ["interval", "start_time", "end_time", "limit"]:
            var = kwargs.get(arg)
            if var is not None:
                params[arg] = var
        return requests.get(
            self.rest_url + "/v1/uiKlines",
            params=params,
        ).json()

    def get_symbol(self, symbol: str) -> Any:
        """
        Get the details of a specific symbol.
        """
        endpoint = f"/v1/ticker/24hr?symbol={symbol}"
        return requests.get(self.rest_url + endpoint).json()[0]

    def get_depth(self, symbol: str, **kwargs) -> Any:
        """
        Get the depth data for a specific product.
        """
        params = {"symbol": symbol}
        for arg in ["limit"]:
            var = kwargs.get(arg)
            if var is not None:
                params[arg] = var
        return requests.get(
            self.rest_url + "/v1/depth",
            params=params,
        ).json()

    def login(self):
        """
        Login to the exchange.
        """
        response = self.create_authenticated_session_with_service()
        if response is None:
            raise Exception("Failed to login")

    def get_session_status(self):
        """
        Get the current session status.
        """
        return requests.get(self.rest_url + "/v1/session/status", headers=self.authenticated_headers).json()

    @property
    def authenticated_headers(self):
        return {
            "cookie": f"connectedAddress={self.session_cookie}",
        }

    def logout(self):
        """
        Logout from the exchange.
        """
        return requests.get(self.rest_url + "/v1/session/logout", headers=self.authenticated_headers).json()

    def get_spot_balances(self):
        """
        Get the spot balances.
        """
        return requests.get(
            self.rest_url + "/v1/balances",
            headers=self.authenticated_headers,
            params={"account": self.public_key, "subAccountId": self.subaccount_id},
        ).json()

    def get_position(self, symbol: str):
        """
        Get the position for a specific symbol.
        """
        return requests.get(
            self.rest_url + "/v1/positionRisk",
            headers=self.authenticated_headers,
            params={
                "symbol": symbol,
                "account": self.public_key,
                "subAccountId": self.subaccount_id,
            },
        ).json()

    def get_approved_signers(self):
        """
        Get the approved signers.
        """
        return requests.get(
            self.rest_url + "/v1/approved-signers",
            headers=self.authenticated_headers,
            params={"account": self.public_key, "subAccountId": self.subaccount_id},
        ).json()

    def get_open_orders(
        self,
        symbol: str = None,
    ):
        """
        Get the open orders.
        """
        params = {"account": self.public_key, "subAccountId": self.subaccount_id}
        if symbol is not None:
            params["symbol"] = symbol
        return requests.get(
            self.rest_url + "/v1/openOrders",
            headers=self.authenticated_headers,
            params=params,
        ).json()

    def get_orders(self, symbol: str = None, ids: List[str] = None):
        """
        Get the open orders.
        """
        params = {"account": self.public_key, "subAccountId": self.subaccount_id}

        if ids is not None:
            params["ids"] = ids
        if symbol is not None:
            params["symbol"] = symbol

        response = requests.get(
            self.rest_url + "/v1/orders",
            headers=self.authenticated_headers,
            params=params,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get orders: {response.text} {response.status_code} " + f"{self.rest_url} {params}"
            )
        return response.json()

    def deposit(self, subaccount_id: int, quantity: int, asset: str = "USDB"):
        """
        Deposit an asset.
        """
        # we need to check if we have sufficient balance to deposit
        required_wei = int(Decimal(str(quantity)) * Decimal(1e18))
        # we check the approvals
        asset_contract = self.get_contract(asset)

        approved_amount = asset_contract.functions.allowance(
            self.public_key, self.get_contract_address("PROTOCOL")
        ).call()
        if approved_amount < required_wei:
            txn = asset_contract.functions.approve(
                self.get_contract_address("PROTOCOL"), required_wei
            ).build_transaction(
                {
                    "from": self.public_key,
                    "nonce": self.web3.eth.get_transaction_count(self.public_key),
                }
            )
            signed_txn = self.wallet.sign_transaction(txn)
            result = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            # we wait for the transaction to be mined
            self.wait_for_transaction(result)

        protocol_contract = self.get_contract("PROTOCOL")
        txn = protocol_contract.functions.deposit(
            self.public_key,
            subaccount_id,
            required_wei,
            asset_contract.address,
        ).build_transaction(
            {
                "from": self.public_key,
                "nonce": self.web3.eth.get_transaction_count(self.public_key),
            }
        )
        signed_txn = self.wallet.sign_transaction(txn)
        result = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.wait_for_transaction(result)

    def wait_for_transaction(self, txn_hash, timeout=60):
        while True:
            if timeout == 0:
                raise Exception("Timeout")
            try:
                receipt = self.web3.eth.get_transaction_receipt(txn_hash)
                if receipt is not None:
                    break
            except TransactionNotFound:
                time.sleep(1)
            timeout -= 1
        return receipt["status"] == 1

    def get_contract_address(self, name: str):
        """
        Get the contract address for a specific asset.
        """
        return self.web3.to_checksum_address(CONTRACTS[self.env][name])

    def get_contract(self, name: str):
        """
        Get the contract for a specific asset.
        """
        abis = {
            "USDB": ERC_20_ABI,
            "PROTOCOL": PROTOCOL_ABI,
        }
        return self.web3.eth.contract(
            address=self.get_contract_address(name),
            abi=abis[name],
        )
