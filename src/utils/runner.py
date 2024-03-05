from loguru import logger

from src.modules.syncswap.syncswap import SyncSwapSwap
from config import *


async def process_sync_swap_swap(private_key: str) -> None:
    from_token = SyncSwapConfig.from_token
    to_token = SyncSwapConfig.to_token
    amount = SyncSwapConfig.amount
    use_percentage = SyncSwapConfig.use_percentage
    swap_percentage = SyncSwapConfig.swap_percentage
    swap_all_balance = SyncSwapConfig.swap_all_balance

    sync_swap = SyncSwapSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount=amount,
        use_percentage=use_percentage,
        swap_percentage=swap_percentage,
        swap_all_balance=swap_all_balance
    )
    logger.info(sync_swap)
    await sync_swap.swap()
