from dataclasses import dataclass

from web3.types import TxParams
from eth_typing import Address
from web3.eth import AsyncEth
from hexbytes import HexBytes
from web3 import AsyncWeb3

from src.utils.user.utils import Utils
from src.utils.data.chains import ERA


@dataclass
class Wallet:
    address: Address
    private_key: str


class Account(Utils):
    def __init__(self, private_key: str, rpc=ERA.rpc) -> None:
        self.private_key = private_key

        self.web3 = AsyncWeb3(
            provider=AsyncWeb3.AsyncHTTPProvider(
                endpoint_uri=rpc,
            ),
            modules={'eth': (AsyncEth,)},
            middlewares=[]
        )
        self.account = self.web3.eth.account.from_key(private_key)
        self.wallet_address = self.account.address

        super().__init__()

    async def get_wallet_balance(self, token: str, stable_address: str) -> float:
        if token.lower() != 'eth':
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(stable_address),
                                              abi=self.load_abi('erc20'))
            balance = await contract.functions.balanceOf(self.wallet_address).call()
        else:
            balance = await self.web3.eth.get_balance(self.wallet_address)

        return balance

    async def sign_transaction(self, tx: TxParams) -> HexBytes:
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        return tx_hash

    async def get_tx_data(self, value: int = 0):
        tx = {
            "chainId": await self.web3.eth.chain_id,
            "from": self.wallet_address,
            "value": value,
            "gasPrice": await self.web3.eth.gas_price,
            "nonce": await self.web3.eth.get_transaction_count(self.wallet_address),
        }
        return tx
