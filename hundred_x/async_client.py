"""
Async client for the HundredX API
"""

from typing import Any

import httpx

from hundred_x.client import HundredXClient
from hundred_x.exceptions import ClientError
from hundred_x.utils import from_message_to_payload


class AsyncHundredXClient(HundredXClient):
    """
    Asynchronous client for the HundredX API.
    """

    async def get_symbol(self, symbol: str = None):
        """
        Get the symbol infos.
        If symbol is None, return all symbols.
        """
        response = await super().get_symbol(symbol)
        if symbol:
            return response[0]
        else:
            return response

    async def get_depth(self, symbol: str, **kwargs) -> Any:
        """
        Get the depth for a specific symbol.
        """
        return await super().get_depth(symbol, **kwargs)

    async def get_trade_history(self, symbol: str, lookback: int = 10, **kwargs) -> Any:
        """
        Get the trade history for a specific symbol.
        if symbol is None, return all trade history.
        """
        return await super().get_trade_history(symbol, lookback, **kwargs)

    async def get_position(self, symbol: str = None):
        """
        Get the position for a specific symbol.
        """
        return await super().get_position(symbol)

    async def get_spot_balances(self):
        """
        Get the spot balances.
        """
        return await super().get_spot_balances()

    async def get_open_orders(self, symbol: str = None):
        """
        Get the open orders for a specific symbol.
        """
        return await super().get_open_orders(symbol)

    async def create_order(self, *args, **kwargs):
        """
        Create and send order.
        """
        return await super().create_order(*args, **kwargs)

    async def cancel_order(self, *args, **kwargs):
        """
        Cancel an order.
        """
        return await super().cancel_order(*args, **kwargs)

    async def cancel_and_replace_order(self, *args, **kwargs):
        """
        Cancel and replace an order.
        """
        return await super().cancel_and_replace_order(*args, **kwargs)

    async def cancel_all_orders(self, subaccount_id: int, product_id: int):
        """
        Cancel all orders.
        """
        return await super().cancel_all_orders(subaccount_id, product_id)

    async def send_message_to_endpoint(
        self, endpoint: str, method: str, message: dict = {}, authenticated: bool = True, params: dict = {}
    ):
        """
        Send a message to an endpoint.
        """
        if not self._validate_function(
            endpoint,
        ):
            raise ClientError(f"Invalid endpoint: {endpoint}")
        payload = from_message_to_payload(message)

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                self.rest_url + endpoint,
                params=params,
                headers={} if not authenticated else self.authenticated_headers,
                json=payload,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to send message: {response.text} {response.status_code} {self.rest_url} {payload}"
                )
            return response.json()
