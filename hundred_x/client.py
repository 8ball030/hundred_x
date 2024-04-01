"""

Client class is a wrapper around the REST API of the exchange. It provides methods to interact with the exchange API.
"""

import time
from typing import Any, List

import eth_account
import requests
from eip712_structs import make_domain
from eth_account.messages import encode_structured_data
from web3 import Web3
from web3.exceptions import TransactionNotFound

from hundred_x.constants import CONTRACTS, ENV_TO_BASE_URL, ENV_TO_WEBSOCKET_URL, LOGIN_MESSAGE
from hundred_x.eip_712 import CancelOrder, CancelOrders, LoginMessage, Order, Withdraw
from hundred_x.enums import Environment, OrderSide, OrderType, TimeInForce
from hundred_x.utils import get_abi

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


PROTOCOL_ABI = get_abi("protocol")
ERC_20_ABI = get_abi("erc20")


VERIFYING_CONTRACT = "0x65CbB566D1A6E60107c0c7888761de1AdFa1ccC0"
CHAIN_ID = 168587773


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
        self.domain = make_domain(
            name="100x",
            version="0.0.0",
            chainId=CHAIN_ID,
            verifyingContract=VERIFYING_CONTRACT,
        )
        self.env = env
        self.rest_url = ENV_TO_BASE_URL[env]
        self.websocket_url = ENV_TO_WEBSOCKET_URL[env]
        self.wallet = eth_account.Account.from_key(private_key)
        self.public_key = self.wallet.address
        self.subaccount_id = subaccount_id
        self.session_cookie = {}
        self.web3 = Web3(Web3.HTTPProvider("https://sepolia.blast.io"))

    def _current_timestamp(self):
        timestamp_ms = int(time.time() * 1000)
        return timestamp_ms

    def _generate_eip_712_login_message(self):
        login_message = LoginMessage(
            account=self.public_key,
            message=LOGIN_MESSAGE,
            timestamp=self._current_timestamp(),
        )
        return login_message.to_message(self.domain)

    def _sign_eip_712_login_message(self, login_data: dict):
        signable_message = encode_structured_data(login_data)
        signed = self.wallet.sign_message(signable_message)
        return signed

    def _extract_message_append_signature(self, login_message, signed):
        signature = signed.signature
        message = login_message["message"]
        message["signature"] = signature.hex()
        return message

    def _generate_authenticate_payload(self):
        login_message = self._generate_eip_712_login_message()
        signed = self._sign_eip_712_login_message(login_message)
        message = self._extract_message_append_signature(login_message, signed)
        return message

    def generate_withdrawal_message(self, subaccount_id: int, quantity: int, asset: str = "USDB"):
        """
        Withdraw an asset.
        """
        ts = self._get_nonce()
        quantity = int(quantity * 1e18)

        shared_params = {
            "account": self.public_key,
            "asset": self.get_contract_address(asset),
            "subAccountId": subaccount_id,
        }
        withdrawal_message = Withdraw(quantity=quantity, nonce=ts, **shared_params)
        message = withdrawal_message.to_message(self.domain)

        signable_message = encode_structured_data(message)
        signed = self.wallet.sign_message(signable_message)

        message["message"]["signature"] = signed.signature.hex()

        return message["message"]

    def withdraw(self, subaccount_id: int, quantity: int, asset: str = "USDB"):
        """
        Generate a withdrawal message and sign it.
        """

        message = self.generate_withdrawal_message(subaccount_id, quantity, asset)

        body = {
            "account": message["account"],
            "asset": message["asset"],
            "subAccountId": message["subAccountId"],
            "quantity": str(message["quantity"]),
            "nonce": message["nonce"],
            "signature": message["signature"],
        }

        res = requests.post(
            self.rest_url + "/v1/withdraw",
            headers=self.authenticated_headers,
            json=body,
        )
        if res.status_code != 200:
            raise Exception(f"Failed to withdraw: `{res.text}` code: {res.status_code} {self.rest_url} ")
        return res.json()

    def _get_nonce(self):
        return int(time.time() * 1000)

    def generate_order_message(
        self,
        subaccount_id: int,
        product_id: int,
        quantity: int,
        price: int,
        side: OrderSide,
        order_type: OrderType,
        time_in_force: TimeInForce,
    ):
        """
        Create an order.
        """
        timestamp_ms = self._get_nonce()

        expiration = (timestamp_ms + 1000 * 60 * 60 * 24) * 1000

        order_message = Order(
            account=self.public_key,
            subAccountId=subaccount_id,
            productId=product_id,
            isBuy=side.value,
            orderType=order_type.value,
            timeInForce=time_in_force.value,
            expiration=expiration,
            price=int(price * 1e18),
            quantity=int(quantity * 1e18),
            nonce=timestamp_ms,
        )

        message = order_message.to_message(self.domain)
        signable_message = encode_structured_data(message)
        signed = self.wallet.sign_message(signable_message)
        message["message"]["signature"] = signed.signature.hex()
        return message["message"]

    def create_order(
        self,
        subaccount_id: int,
        product_id: int,
        quantity: int,
        price: int,
        side: OrderSide,
        order_type: OrderType,
        time_in_force: TimeInForce,
    ):
        """
        Create an order.
        """
        message = self.generate_order_message(
            subaccount_id, product_id, quantity, price, side, order_type, time_in_force
        )

        payload = {
            "account": message["account"],
            "subAccountId": message["subAccountId"],
            "productId": message["productId"],
            "isBuy": message["isBuy"],
            "orderType": message["orderType"],
            "timeInForce": message["timeInForce"],
            "expiration": message["expiration"],
            "price": str(message["price"]),
            "quantity": str(message["quantity"]),
            "nonce": message["nonce"],
            "signature": message["signature"],
        }
        res = requests.post(
            self.rest_url + "/v1/order",
            headers=self.authenticated_headers,
            json=payload,
        )
        # breakpoint()
        # # we now try to verify the signature

        if res.status_code != 200:
            raise Exception(f"Failed to create order: `{res.text}` {res.status_code} {self.rest_url} {payload}")
        return res.json()

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
        message = self.generate_order_message(
            subaccount_id, product_id, quantity, price, side, order_type, time_in_force
        )
        payload = {
            "account": message["account"],
            "subAccountId": message["subAccountId"],
            "productId": message["productId"],
            "isBuy": message["isBuy"],
            "orderType": message["orderType"],
            "timeInForce": message["timeInForce"],
            "expiration": message["expiration"],
            "price": str(message["price"]),
            "quantity": str(message["quantity"]),
            "nonce": message["nonce"],
            "signature": message["signature"],
            "idToCancel": order_id_to_cancel,
        }
        res = requests.post(
            self.rest_url + "/v1/order/cancel-and-replace",
            headers=self.authenticated_headers,
            json=payload,
        )

        if res.status_code != 200:
            raise Exception(f"Failed to create order: `{res.text}` {res.status_code} {self.rest_url} {payload}")
        return res.json()

    def generate_cancel_order_msg(self, subaccount_id: int, product_id: int, order_id: int):
        """
        Cancel an order.
        """
        cancel_order_message = CancelOrder(
            account=self.public_key,
            subAccountId=subaccount_id,
            productId=product_id,
            orderId=order_id,
        )
        message = cancel_order_message.to_message(self.domain)
        signable_message = encode_structured_data(message)
        signed = self.wallet.sign_message(signable_message)
        message["message"]["signature"] = signed.signature.hex()
        return message["message"]

    def cancel_order(self, subaccount_id: int, product_id: int, order_id: int):
        """
        Cancel an order.
        """
        message = self.generate_cancel_order_msg(subaccount_id, product_id, order_id)
        body = {
            "account": message["account"],
            "subAccountId": message["subAccountId"],
            "productId": message["productId"],
            "orderId": message["orderId"],
            "signature": message["signature"],
        }
        res = requests.delete(
            self.rest_url + "/v1/order",
            headers=self.authenticated_headers,
            json=body,
        )
        if res.status_code != 200:
            raise Exception(f"Failed to cancel order: {res.text} {res.status_code} {self.rest_url} {body}")
        return res.json()

    def generate_all_orders_message(self, subaccount_id: int, product_id: int):
        """
        Cancel all orders.
        """
        cancel_order_message = CancelOrders(
            account=self.public_key,
            subAccountId=subaccount_id,
            productId=product_id,
        )
        message = cancel_order_message.to_message(self.domain)
        signable_message = encode_structured_data(message)
        signed = self.wallet.sign_message(signable_message)
        message["message"]["signature"] = signed.signature.hex()
        return message["message"]

    def cancel_all_orders(self, subaccount_id: int, product_id: int):
        """
        Cancel all orders.
        """
        message = self.generate_all_orders_message(subaccount_id, product_id)
        body = {
            "account": message["account"],
            "subAccountId": message["subAccountId"],
            "productId": message["productId"],
            "signature": message["signature"],
        }
        res = requests.delete(
            self.rest_url + "/v1/openOrders",
            headers=self.authenticated_headers,
            json=body,
        )
        if res.status_code != 200:
            raise Exception(f"Failed to cancel all orders: {res.text} {res.status_code} {self.rest_url} {body}")
        return res.json()

    def create_authenticated_session_with_service(self):
        login_payload = self._generate_authenticate_payload()
        headers = {
            "Content-type": "application/json",
        }
        response = requests.post(self.rest_url + "/v1/session/login", headers=headers, json=login_payload)

        if response.status_code != 200:
            raise Exception(
                f"Failed to authenticate with 100x: {response.text} {response.status_code} "
                + f"{self.rest_url} {login_payload}"
            )
        self.session_cookie = response.json().get("value")
        response = response.json()
        return response

    def list_products(self) -> List[Any]:
        """
        Get a list of all available products.
        """
        endpoint = "/v1/products"

        return requests.get(self.rest_url + endpoint).json()

    def get_product(self, product_symbol: str) -> Any:
        """
        Get the details of a specific product.
        """
        endpoint = f"/v1/products/{product_symbol}"
        return requests.get(self.rest_url + endpoint).json()

    def get_server_time(self) -> Any:
        """
        Get the server time.
        """
        endpoint = "/v1/time"
        return requests.get(self.rest_url + endpoint).json()

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
        assert response is not None

    def get_session_status(self):
        """
        Get the current session status.
        """
        response = requests.get(self.rest_url + "/v1/session/status", headers=self.authenticated_headers)
        return response.json()

    @property
    def authenticated_headers(self):
        return {
            "cookie": f"connectedAddress={self.session_cookie}",
        }

    def logout(self):
        """
        Logout from the exchange.
        """
        response = requests.get(self.rest_url + "/v1/session/logout", headers=self.authenticated_headers)
        return response.json()

    def get_spot_balances(self):
        """
        Get the spot balances.
        """
        response = requests.get(
            self.rest_url + "/v1/balances",
            headers=self.authenticated_headers,
            params={"account": self.public_key, "subAccountId": self.subaccount_id},
        )
        return response.json()

    def get_position(self, symbol: str):
        """
        Get the position for a specific symbol.
        """
        response = requests.get(
            self.rest_url + "/v1/positionRisk",
            headers=self.authenticated_headers,
            params={
                "symbol": symbol,
                "account": self.public_key,
                "subAccountId": self.subaccount_id,
            },
        )
        return response.json()

    def get_approved_signers(self):
        """
        Get the approved signers.
        """
        response = requests.get(
            self.rest_url + "/v1/approved-signers",
            headers=self.authenticated_headers,
            params={"account": self.public_key, "subAccountId": self.subaccount_id},
        )
        return response.json()

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
        response = requests.get(
            self.rest_url + "/v1/openOrders",
            headers=self.authenticated_headers,
            params=params,
        )
        return response.json()

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
        required_wei = int(quantity * 1e18)
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
