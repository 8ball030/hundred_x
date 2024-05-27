"""
Constants for the hundred_x package.
"""

from hundred_x.enums import ApiType, Environment

DEVNET_REST_URL = "https://api.dev.ciaobella.dev"
DEVNET_WEBSOCKET_URL = "https://stream.dev.ciaobella.dev"

TESTNET_REST_URL = "https://api.staging.100x.finance"
TESTNET_WEBSOCKET_URL = "https://stream.staging.100x.finance"

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
    Environment.PROD: {
        "USDB": "0x4300000000000000000000000000000000000003",
        "PROTOCOL": "0x1BaEbEE6B00B3f559B0Ff0719B47E0aF22A6bfC4",
        "VERIFYING_CONTRACT": "0x691a5fc3a81a144e36c6C4fBCa1fC82843c80d0d",
        "CHAIN_ID": 81457,
    },
    Environment.TESTNET: {
        "USDB": "0x79A59c326C715AC2d31C169C85d1232319E341ce",
        "PROTOCOL": "0x0c3b9472b3923CfE199bAE24B5f5bD75FAD2bae9",
        "VERIFYING_CONTRACT": "0x02Ca4fcB63E2D3C89fa20D86ccDcfc540c683545",
        "CHAIN_ID": 168587773,
    },
    Environment.DEVNET: {
        "USDB": "0x79A59c326C715AC2d31C169C85d1232319E341ce",
        "PROTOCOL": "0x9E4d21FeFE19EbD9ce94b71A60bce6CD793DD2BF",
        "VERIFYING_CONTRACT": "0x8ffdD4755aa383cD4CB715ABD8e1375926123729",
        "CHAIN_ID": 168587773,
    },
}
