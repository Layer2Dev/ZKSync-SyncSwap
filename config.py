MIN_PAUSE = 30
MAX_PAUSE = 70
SLIPPAGE = 0.03
CHECK_GWEI = True
MAX_GWEI = 50

RETRIES = 3
PAUSE_BETWEEN_RETRIES = 1

syncswap_swap = True


class SyncSwapConfig:
    from_token = 'ETH'
    to_token = 'USDC'
    amount = [0.0005, 0.001]
    use_percentage = False
    swap_percentage = [0.4, 0.6]
    swap_all_balance = False
