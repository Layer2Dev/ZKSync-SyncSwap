from typing import (
    Union,
    List,
)

from web3.contract import Contract
from eth_typing import Address
from web3 import AsyncWeb3

from src.utils.base_swap import BaseSwap
from src.utils.data.types import Types
from src.utils.data.contracts import (
    contracts,
    abi_names,
)

from src.modules.syncswap.utils.transaction_data import (
    get_amount_out,
    create_swap_tx,
)


class SyncSwapSwap(BaseSwap):
    def __init__(self, private_key: str, from_token: str, to_token: Union[str, List[str]],
                 amount: Union[float, List[float]], use_percentage: bool, swap_percentage: Union[float, List[float]],
                 swap_all_balance: bool) -> None:

        contract_address = contracts['syncswap']['router']
        abi_name = abi_names['syncswap']['router']
        dex_name = self.__class__.__name__

        super().__init__(private_key, from_token, to_token, amount, use_percentage, swap_percentage, swap_all_balance,
                         contract_address, abi_name, dex_name)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.wallet_address} | {self.from_token} => {self.to_token}'

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address) -> int:
        return await get_amount_out(self.web3, from_token_address, to_token_address, amount, self.wallet_address)

    async def create_swap_tx(self, from_token: str, to_token: str, contract: Contract, amount_out: int,
                             from_token_address: str, to_token_address: str, account_address: Address, amount: int,
                             web3: AsyncWeb3) -> Types.SwapTransaction:
        return await create_swap_tx(from_token, contract, from_token_address, to_token_address,
                                    account_address, amount, web3)
