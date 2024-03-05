from typing import (
    Awaitable,
    Callable,
    Optional,
    Union,
)

from random import uniform
from asyncio import sleep
import json

from web3.contract import Contract
from web3.types import TxParams
from web3 import AsyncWeb3
import loguru

from eth_typing import (
    Address,
    HexStr,
)

from src.utils.logger import Logger


class Utils:
    def __init__(self) -> None:
        self.logger = Logger(loguru.logger)

    def load_contract(self, address: str, web3: AsyncWeb3, abi_name: str) -> Optional[Contract]:
        if address is None:
            return

        address = web3.to_checksum_address(address)
        return web3.eth.contract(address=address, abi=self.load_abi(abi_name))

    async def get_decimals(self, contract_address: Contract, web3: AsyncWeb3) -> int:
        contract = self.load_contract(contract_address, web3, 'erc20')
        decimals = await contract.functions.decimals().call()
        return decimals

    async def approve_token(self, amount: float, private_key: str, from_token_address: str, spender: str,
                            address_wallet: Address, web3: AsyncWeb3) -> Optional[HexStr]:
        try:
            spender = web3.to_checksum_address(spender)
            contract = self.load_contract(from_token_address, web3, 'erc20')
            allowance_amount = await self.check_allowance(web3, from_token_address, address_wallet, spender)

            if amount > allowance_amount:
                self.logger.debug('🛠️ | Approving token...')
                tx = await contract.functions.approve(
                    spender,
                    100000000000000000000000000000000000000000000000000000000000000000000000000000
                ).build_transaction(
                    {
                        'chainId': await web3.eth.chain_id,
                        'from': address_wallet,
                        'nonce': await web3.eth.get_transaction_count(address_wallet),
                        'gasPrice': 0,
                        'gas': 0,
                        'value': 0
                    }
                )

                gas_price = await self.add_gas_price(web3)
                tx['gasPrice'] = gas_price

                gas_limit = await self.add_gas_limit(web3, tx)
                tx['gas'] = gas_limit

                signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
                raw_tx_hash = await web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = await web3.eth.wait_for_transaction_receipt(raw_tx_hash)
                while tx_receipt is None:
                    await sleep(1)
                    tx_receipt = await web3.eth.get_transaction_receipt(raw_tx_hash)
                tx_hash = web3.to_hex(raw_tx_hash)
                self.logger.success(f'✔️ | Token approved')
                await sleep(5)
                return tx_hash

        except Exception as ex:
            self.logger.error(f'Something went wrong | {ex}')

    async def check_allowance(self, web3: AsyncWeb3, from_token_address: str, address_wallet: Address, spender: str
                              ) -> Optional[int]:
        try:
            contract = web3.eth.contract(address=web3.to_checksum_address(from_token_address),
                                         abi=self.load_abi('erc20'))
            amount_approved = await contract.functions.allowance(address_wallet, spender).call()
            return amount_approved

        except Exception as ex:
            self.logger.error(f'Something went wrong | {ex}')

    async def add_gas_price(self, web3: AsyncWeb3) -> Optional[int]:
        try:
            gas_price = await web3.eth.gas_price
            gas_price = int(gas_price * uniform(1.01, 1.02))
            return gas_price
        except Exception as ex:
            self.logger.error(f'Something went wrong | {ex}')

    async def setup_decimals(self, from_token: str, from_token_address: str, web3: AsyncWeb3
                             ) -> Union[int, Callable[[str, AsyncWeb3], Awaitable[int]]]:
        if from_token.lower() == 'eth' or from_token.lower() == 'weth':
            return 18
        else:
            return await self.get_decimals(from_token_address, web3)

    async def create_amount(self, from_token: str, from_token_address: str, web3: AsyncWeb3, amount: float) -> int:
        decimals = await self.setup_decimals(from_token, from_token_address, web3)
        amount = int(amount * 10 ** decimals)
        return amount

    @staticmethod
    def create_liquidity_remove_amount(balance: int, remove_all: bool, removing_percentage: float) -> int:
        if remove_all is True:
            amount = balance
        else:
            amount = int(balance * removing_percentage)

        return amount

    @staticmethod
    async def add_gas_limit(web3: AsyncWeb3, tx: TxParams) -> int:
        tx['value'] = 0
        gas_limit = await web3.eth.estimate_gas(tx)
        return gas_limit

    @staticmethod
    def load_abi(name: str) -> str:
        with open(f'./assets/abi/{name}.json') as f:
            abi: str = json.load(f)
        return abi
