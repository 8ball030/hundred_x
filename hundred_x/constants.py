"""
Constants for the hundred_x package.
"""

from hundred_x.enums import ApiType, Environment

DEVNET_REST_URL = "https://api.dev.ciaobella.dev"
DEVNET_WEBSOCKET_URL = "https://stream.dev.ciaobella.dev"

TESTNET_REST_URL = "https://staging.100x.finance"
TESTNET_WEBSOCKET_URL = "https://staging.100x.finance"

MAINNET_REST_URL = "https://api.100x.finance"
MAINNET_WEBSOCKET_URL = "https://stream.100x.finance"


APIS = {
    Environment.TESTNET: {
        ApiType.REST: TESTNET_REST_URL,
        ApiType.WEBSOCKET: TESTNET_WEBSOCKET_URL,
    },
    Environment.PROD: {
        ApiType.REST: MAINNET_REST_URL,
        ApiType.WEBSOCKET: MAINNET_WEBSOCKET_URL,
    },
    Environment.DEVNET: {
        ApiType.REST: DEVNET_REST_URL,
        ApiType.WEBSOCKET: DEVNET_WEBSOCKET_URL,
    },
}


LOGIN_MESSAGE = "I would like to login to 100x finance."

CONTRACTS = {
    Environment.TESTNET: {
        "USDB": "0x79A59c326C715AC2d31C169C85d1232319E341ce",
        "PROTOCOL": "0x63bD0ca355Cfc117F5176E5eF3e34A6D60081937",
        "VERIFYING_CONTRACT": "0x65CbB566D1A6E60107c0c7888761de1AdFa1ccC0",
        "CHAIN_ID": 168587773,
    },
    Environment.DEVNET: {
        "USDB": "0x79A59c326C715AC2d31C169C85d1232319E341ce",
        "PROTOCOL": "0x2c72Fbefcc6D23553EC4E209E7b23E118718a239",
        "VERIFYING_CONTRACT": "0xFA322Cd45159384132C3D191618556349bA3bF53",
        "CHAIN_ID": 168587773,
    },
}
