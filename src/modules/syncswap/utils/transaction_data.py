from time import time

from web3.contract import Contract
from web3.types import TxParams
from eth_typing import Address
from web3 import AsyncWeb3
from loguru import logger
from eth_abi import abi

from src.utils.user.utils import Utils
from config import SLIPPAGE

from src.utils.data.contracts import (
    contracts,
    abi_names,
)


async def get_amount_out(web3: AsyncWeb3, from_token_address: str, to_token_address: str, amount: int,
                         account_address: Address) -> int:
    pool_address = await get_pool(web3, from_token_address, to_token_address)
    utils = Utils()
    pool_contract = utils.load_contract(pool_address, web3, abi_names['syncswap']['classic_pool'])

    amount_out = await pool_contract.functions.getAmountOut(
        web3.to_checksum_address(from_token_address),
        amount,
        account_address
    ).call()
    return int(amount_out * (1 - SLIPPAGE))


async def get_pool(web3: AsyncWeb3, from_token_address: str, to_token_address: str) -> str:
    utils = Utils()
    contract = utils.load_contract(contracts['syncswap']["classic_pool"], web3, abi_names['syncswap']['pool'])

    pool_address = await contract.functions.getPool(
        web3.to_checksum_address(from_token_address),
        web3.to_checksum_address(to_token_address)
    ).call()

    return pool_address


async def create_swap_tx(from_token: str, contract: Contract, from_token_address: str, to_token_address: str,
                         account_address: Address, amount: int, web3: AsyncWeb3) -> TxParams:
    pool_address = await get_pool(web3, from_token_address, to_token_address)
    if pool_address == '0x0000000000000000000000000000000000000000':
        logger.error(f'Pool does not exist!')
        return

    min_amount_out = await get_amount_out(web3, from_token_address, to_token_address, amount, account_address)

    steps = [{
        "pool": pool_address,
        "data": abi.encode(["address", "address", "uint8"], [from_token_address, account_address, 1]),
        "callback": '0x0000000000000000000000000000000000000000',
        "callbackData": "0x"
    }]

    paths = [{
        "steps": steps,
        "tokenIn": '0x0000000000000000000000000000000000000000' if from_token.upper() == "ETH" else from_token_address,
        "amountIn": amount
    }]

    deadline = int(time()) + 1000000

    contract_txn = await contract.functions.swap(
        paths,
        min_amount_out,
        deadline
    ).build_transaction({
        'from': account_address,
        'value': amount if from_token.upper() == 'ETH' else 0,
        'nonce': await web3.eth.get_transaction_count(account_address),
        "gasPrice": await web3.eth.gas_price,
    })

    return contract_txn
