"""
Async client for the HundredX API
"""
from typing import Any
import httpx
import requests
from decimal import Decimal

from hundred_x.client import HundredXClient
from hundred_x.eip_712 import Order, CancelOrders, CancelOrder, LoginMessage
from hundred_x.constants import LOGIN_MESSAGE
from hundred_x.enums import OrderSide, OrderType, TimeInForce
from hundred_x.utils import from_message_to_payload, get_abi

class AsyncHundredXClient(HundredXClient):
    """
    Asynchronous client for the HundredX API.
    """

    async def get_symbol_info(self, symbol: str):
        """
        Get the symbol info for a specific symbol.
        """
        response = await self.send_message_to_endpoint(
            endpoint=f"/v1/ticker/24hr?symbol={symbol}",
            method="GET",
            )
        return response[0]
        
    async def get_depth(self, symbol: str, **kwargs) -> Any:
        """
        Get the depth for a specific symbol.
        """
        params = {
            "symbol": symbol,
            "limit": kwargs.get("limit", 5),
        }
        return await self.send_message_to_endpoint(
            endpoint=f"/v1/depth",
            method="GET",
            message=params,
        )

    async def get_position(self, symbol: str):
        """
        Get the position for a specific symbol.
        """
        message = {
            "symbol": symbol,
            "account": self.public_key,
            "subAccountId": self.subaccount_id,
        }
        return await self.send_message_to_endpoint(
            endpoint="/v1/positionRisk",
            method="GET",
            message=message,
            authenticated=True,
        )

    async def get_spot_balances(self):
        """
        Get the spot balances.
        """
        message = {
            "account": self.public_key,
            "subAccountId": self.subaccount_id,
        }
        return await self.send_message_to_endpoint("/v1/balances", "GET", message)

    async def get_open_orders(self, symbol: str = None):
        """
        Get the open orders for a specific symbol.
        """
        params = {"symbol": symbol, "account": self.public_key, "subAccountId": self.subaccount_id}
        if symbol is None:
            del params["symbol"]
        return await self.send_message_to_endpoint("/v1/openOrders", "GET", params)

    async def create_and_send_order(
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
        Create and send order.
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
        response = await self.send_message_to_endpoint("/v1/order", "POST", message)
        return response

    async def cancel_order(self, product_id: int, order_id: int):
        """
        Cancel an order.
        """
        message = self.generate_and_sign_message(
            CancelOrder,
            subAccountId=self.subaccount_id,
            productId=product_id,
            orderId=order_id,
            **self.get_shared_params(),
        )
        response = await self.send_message_to_endpoint("/v1/order", "DELETE", message)
        return response

    async def cancel_and_replace_order(
        self,
        subaccount_id: int,
        product_id: int,
        quantity: int,
        price: int,
        side: OrderSide,
        order_id_to_cancel: str,
        nonce: int = 0,
    ):
        """
        Cancel and replace an order.
        """
        ts = self._current_timestamp()
        if nonce == 0:
            nonce = ts
        _message = self.generate_and_sign_message(
            Order,
            subAccountId=subaccount_id,
            productId=product_id,
            quantity=int(Decimal(str(quantity)) * Decimal(1e18)),
            price=int(Decimal(str(price)) * Decimal(1e18)),
            isBuy=side.value,
            orderType=OrderType.LIMIT_MAKER.value,
            timeInForce=TimeInForce.GTC.value,
            nonce=nonce,
            expiration=(ts + 1000 * 60 * 60 * 24) * 1000,
            **self.get_shared_params(),
        )
        message = {}
        message["newOrder"] = from_message_to_payload(_message)
        message["idToCancel"] = order_id_to_cancel
        response = await self.send_message_to_endpoint("/v1/order/cancel-and-replace", "POST", message)
        return response
    
    async def cancel_all_orders(self, subaccount_id: int, product_id: int):
        """
        Cancel all orders.
        """
        message = self.generate_and_sign_message(
            CancelOrders,
            subAccountId=subaccount_id,
            productId=product_id,
            **self.get_shared_params(),
        )
        response = await self.send_message_to_endpoint("/v1/openOrders", "DELETE", message)
        return response
    
    async def login(self):
        """
        Login to the exchange.
        """
        response = await self.create_authenticated_session_with_service()
        if response is None:
            raise Exception("Failed to login")

    async def send_message_to_endpoint(self, endpoint: str, method: str, message: dict = {}, authenticated: bool = True):
        """
        Send a message to an endpoint.
        """
        payload = from_message_to_payload(message)
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.request(
                    method,
                    self.rest_url + endpoint,
                    headers={} if not authenticated else self.authenticated_headers,
                    params=payload,
                )
            else:
                response = await client.request(
                    method,
                    self.rest_url + endpoint,
                    headers={} if not authenticated else self.authenticated_headers,
                    json=payload,
                )
            
            if response.status_code != 200:
                raise Exception(f"Failed to send message: {response.text} {response.status_code} {self.rest_url} {payload}")
            return response.json()

    async def create_authenticated_session_with_service(self):
        login_payload = self.generate_and_sign_message(
            LoginMessage,
            message=LOGIN_MESSAGE,
            timestamp=self._current_timestamp(),
            **self.get_shared_params(),
        )
        response = await self.send_message_to_endpoint("/v1/session/login", "POST", login_payload, authenticated=False)
        self.session_cookie = response.get("value")
        return response

    async def list_products(self):
        """
        List all products available on the exchange.
        """
        return super().list_products()

    async def get_product(self, symbol: str):
        """
        Get a specific product available on the exchange.
        """
        return super().get_product(symbol)

    async def get_server_time(self):
        """
        Get the server time.
        """
        return super().get_server_time()
