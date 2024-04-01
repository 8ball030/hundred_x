"""
Utils module for hundred_x package.
"""

import json
import os
from pathlib import Path

from hundred_x.enums import Environment

INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ENCODING = "utf-8"


def get_base_url(envirnment: Environment):
    """Map the environment to the corresponding base URL."""


def get_abi(contract_name: str):
    """Get the ABI of the contract."""
    with open(Path(INSTALL_DIR) / "abis" / f"{contract_name}.json", "r", encoding=DEFAULT_ENCODING) as f:
        return json.load(f)
