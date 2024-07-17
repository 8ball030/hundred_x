import asyncio
import os
from pprint import pprint

from hundred_x.async_client import AsyncHundredXClient
from hundred_x.enums import Environment, OrderSide, OrderType, TimeInForce


async def main():
    """
    Fetch all positions then close them all.
    """
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

    # We check the positions.
    print("Positions")
    response = await client.get_position()
    pprint(response)

    for position in response:
        if int(position['quantity']) > 0:
            # We close the position.

            pos_size = int(position['quantity']) / 1e18
            pos_price = int(int(position['avgEntryPrice']) / 1e18)
            prices = await client.get_symbol(
                symbol=position['productSymbol']
            )  # This is the product_id for the symbol 'btcperp
            exit_price = int(int(prices['markPrice']) / 1e18)

            print(
                f"Closing pos {position['productSymbol']} with size {pos_size} at {pos_price} with price {exit_price}"
            )

            response = await client.create_order(
                subaccount_id=subaccount_id,
                product_id=position['productId'],
                quantity=pos_size,
                side=OrderSide.SELL,
                price=exit_price,
                order_type=OrderType.MARKET,
                time_in_force=TimeInForce.GTC,
            )
            pprint(response)


if __name__ == "__main__":
    asyncio.run(main())
