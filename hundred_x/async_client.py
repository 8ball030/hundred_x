"""
Async client for the HundredX API
"""

from hundred_x.client import HundredXClient


class AsyncHundredXClient(HundredXClient):
    """
    Asynchronous client for the HundredX API.
    """

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
