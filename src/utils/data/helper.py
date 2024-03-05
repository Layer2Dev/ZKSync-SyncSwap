from web3 import Web3

from src.utils.data.mappings import module_handlers

with open('config.py', 'r', encoding='utf-8-sig') as file:
    module_config = file.read()

exec(module_config)

with open('wallets.txt', 'r', encoding='utf-8-sig') as file:
    private_keys = [line.strip() for line in file]

patterns = {}
web3 = Web3(Web3.HTTPProvider('https://1rpc.io/zksync2-era'))

for module in module_handlers:
    if globals().get(module):
        patterns[module] = 'On'
    else:
        patterns[module] = 'Off'

print(f'Loaded {len(private_keys)} wallets:')
print('\033[39m')

for private_key in private_keys:
    print(web3.eth.account.from_key(private_key).address)

for pattern, value in patterns.items():
    if value == 'Off':
        print("\033[31m {}".format(f'{pattern} = {value}'))
    else:
        print("\033[32m {}".format(f'{pattern} = {value}'))
print('\033[39m')

active_module = [module for module, value in patterns.items() if value == 'On']
