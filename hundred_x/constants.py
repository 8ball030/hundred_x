"""
Constants for the hundred_x package.
"""

import os

from hundred_x.enums import ApiType, Environment

DEVNET_REST_URL = os.getenv("DEVNET_REST_URL", None)
DEVNET_WEBSOCKET_URL = os.getenv("DEVNET_WEBSOCKET_URL", None)

TESTNET_REST_URL = "https://api.staging.100x.finance"
TESTNET_WEBSOCKET_URL = "https://stream.staging.100x.finance"

MAINNET_REST_URL = "https://api.100x.finance"
MAINNET_WEBSOCKET_URL = "https://stream.100x.finance"

REFERRAL_CODE = "8baller"

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

RPC_URLS = {
    Environment.DEVNET: os.getenv("DEVNET_RPC_URL", None),
    Environment.TESTNET: "https://sepolia.blast.io",
    Environment.PROD: "https://rpc.blast.io",
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
        "PROTOCOL": "0x9645aD4bE9bAd73B95ae785765e3683e418806A9",
        "VERIFYING_CONTRACT": "0xb87e7d837844F3BbbF043F47E6Ee15B42208F9cd",
        "CHAIN_ID": 168587773,
    },
    Environment.DEVNET: {
        "USDB": "0x79A59c326C715AC2d31C169C85d1232319E341ce",
        "PROTOCOL": "0x9E4d21FeFE19EbD9ce94b71A60bce6CD793DD2BF",
        "VERIFYING_CONTRACT": "0x8ffdD4755aa383cD4CB715ABD8e1375926123729",
        "CHAIN_ID": 168587773,
    },
}
