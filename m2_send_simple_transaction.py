import binascii
import asyncio

import pprint
import aioethereum

import settings
from utils import get_tx_until_mined

loop = asyncio.get_event_loop()


async def unlock_send_and_get_transaction(client, data, pswd):
    # 1. Unlock account
    await client.personal_unlockAccount(data['from_'], pswd)

    # 2. Make send transaction to the node
    tx_id = await client.eth_sendTransaction(**data)

    # 3. Lock back account
    await client.personal_lockAccount(data['from_'])

    print("Transaction hash: %s" % tx_id)
    print("Transaction data:")
    pprint.pprint(data)

    print("Waiting until mined..")
    tx_data = await get_tx_until_mined(client, tx_id)

    print("Transaction data:")
    pprint.pprint(tx_data)


async def main():
    # prepare payload data
    data = {
        'from_': settings.SENDER_ADDRESS,
        'to': '0xde5e2aab4a04f5c3b6b39fde028dc592bb7b902b',
        'data': '0x' + binascii.hexlify(b'Empty msg').decode('utf-8'),
        'gas': 22000,
        'gas_price': 0,
        'value': 0.1
    }
    # retrieve a password for unlock mechanizm
    with open('./node_db/pswd.txt', 'r') as reader:
        pswd = reader.read()

    client = await aioethereum.create_ethereum_client(settings.NODE_URL, loop=loop)
    await unlock_send_and_get_transaction(client, data, pswd)


if __name__ == '__main__':
    loop.run_until_complete(main())
