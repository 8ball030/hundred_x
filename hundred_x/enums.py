"""
Enmum for the hundred_x package
"""

from enum import Enum


class ApiType(Enum):
    """
    Enum for the API type.
    """

    REST = "REST"
    WEBSOCKET = "WEBSOCKET"


class Environment(Enum):
    """
    Enum for the environment of the client.
    """

    PROD = "prod"
    TESTNET = "testnet"
    DEVNET = "local"


class OrderType(Enum):
    """
    Enum for the order type.
    """

    LIMIT = 0
    LIMIT_MAKER = 1
    MARKET = 2
    STOP_LOSS = 3
    STOP_LOSS_LIMIT = 4
    TAKE_PROFIT = 5
    TAKE_PROFIT_LIMIT = 6


class TimeInForce(Enum):
    """
    Enum for the time in force.
    """

    GTC = 0
    FOK = 1
    IOC = 2


class OrderSide(Enum):
    """
    Enum for the order side.
    """

    BUY = True
    SELL = False
