"""
Example of a client that connects to a server and sends a message.
"""

import asyncio
import os
from pprint import pprint

from hundred_x.async_client import AsyncHundredXClient
from hundred_x.enums import Environment, OrderSide, OrderType, TimeInForce


async def main():
    key = os.getenv("HUNDRED_X_PRIVATE_KEY")
    subaccount_id = 0

    if not key:
        raise ValueError("HUNDRED_X_PRIVATE_KEY environment variable is not set.")

    client = AsyncHundredXClient(Environment.PROD, key, subaccount_id=subaccount_id)

    print(f"Using Wallet: {client.public_key}")
    print(f"Using Subaccount ID: {client.subaccount_id}")

    # In order to hit the authenticated endpoints, we need to login.
    # We check the initial balance.
    print("Initial Balance")
    response = await client.get_spot_balances()
    pprint(response)

    # We first get the symbol.
    print("Symbol")
    response = await client.get_symbol("btcperp")
    pprint(response)

    # We create an order.
    print("Create Order")
    response = await client.create_order(
        subaccount_id=subaccount_id,
        product_id=response['productId'],  # This is the product_id for the symbol 'btcperp
        quantity=0.0001,
        price=round(int(response['markPrice']) * 0.99 / 1e18),  # This is the current price of the symbol 'btcperp'
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
    )

    # We check the open orders.
    print("Open Orders")
    response = await client.get_open_orders("btcperp")
    pprint(response)

    # We cancel the order.
    print("Cancel Order")
    response = await client.cancel_order(order_id=response[0]["id"], product_id=response[0]["productId"])
    pprint(response)

    # We check the positions.
    print("Positions")
    response = await client.get_position()
    pprint(response)

    # We check if we can cancel and replace an order.
    # We check the open orders.
    print("Open Orders")
    response = await client.get_open_orders("btcperp")
    pprint(response)

    # We create an order.
    print("Create Order")

    response = await client.create_order(
        subaccount_id=subaccount_id,
        product_id=response[0]["productId"],
        quantity=0.001,
        price=round(int(response[0]["price"]) * 0.99 / 1e18),
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
    )

    # We check the open orders.
    print("Open Orders")
    response = await client.get_open_orders("btcperp")
    pprint(response)

    # We cancel and replace the order.
    print("Cancel and Replace Order")
    response = await client.cancel_and_replace_order(
        order_id_to_cancel=response[0]["id"],
        product_id=response[0]["productId"],
        quantity=0.002,
        price=round(int(response[0]["price"]) * 0.99 / 1e18),
        side=OrderSide.BUY,
    )
    pprint(response)

    # We cancel all orders.
    response = await client.cancel_all_orders(subaccount_id=subaccount_id, product_id=1002)


if __name__ == "__main__":
    asyncio.run(main())
