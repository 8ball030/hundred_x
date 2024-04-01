"""
Constants for the hundred_x package.
"""

from hundred_x.enums import Environment

TESTNET_REST_URL = "https://api.ciaobella.dev"
TESTNET_WEBSOCKET_URL = "https://stream.ciaobella.dev"


ENV_TO_BASE_URL = {
    Environment.TESTNET: TESTNET_REST_URL,
}

ENV_TO_WEBSOCKET_URL = {
    Environment.TESTNET: TESTNET_WEBSOCKET_URL,
}

LOGIN_MESSAGE = "I would like to login to 100x finance."

CONTRACTS = {
    Environment.TESTNET: {
        "USDB": "0x79A59c326C715AC2d31C169C85d1232319E341ce",
        "PROTOCOL": "0x63bD0ca355Cfc117F5176E5eF3e34A6D60081937",
    },
}
