"""
Eip structs for the hundred_x project

"""

from eip712_structs import Address, Boolean, EIP712Struct, String, Uint


class LoginMessage(EIP712Struct):
    account = Address()
    message = String()
    timestamp = Uint(64)


class Withdraw(EIP712Struct):
    account = Address()
    subAccountId = Uint(8)
    asset = Address()
    quantity = Uint(128)
    nonce = Uint(64)


class Order(EIP712Struct):
    account = Address()
    subAccountId = Uint(8)
    productId = Uint(32)
    isBuy = Boolean()
    orderType = Uint(8)
    timeInForce = Uint(8)
    expiration = Uint(64)
    price = Uint(128)
    quantity = Uint(128)
    nonce = Uint(64)


class CancelOrder(EIP712Struct):
    account = Address()
    subAccountId = Uint(8)
    productId = Uint(32)
    orderId = String()


class CancelOrders(EIP712Struct):
    account = Address()
    subAccountId = Uint(8)
    productId = Uint(32)
