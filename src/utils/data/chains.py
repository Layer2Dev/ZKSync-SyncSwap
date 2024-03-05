class Chain:
    def __init__(self, chain_id: int, rpc: str, scan: str) -> None:
        self.chain_id = chain_id
        self.rpc = rpc
        self.scan = scan


ETH = Chain(
    chain_id=1,
    rpc='https://rpc.ankr.com/eth',
    scan='https://etherscan.io/tx'
)

ERA = Chain(
    chain_id=324,
    rpc='https://zksync-era.blockpi.network/v1/rpc/public',
    scan='https://explorer.zksync.io/tx'
)

chain_mapping = {
    'eth': ETH,
    'era': ERA
}
