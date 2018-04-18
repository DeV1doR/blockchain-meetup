import asyncio
import pprint

import aioethereum

import settings
from utils import get_address, MTransaction, to_hex, get_tx_until_mined

loop = asyncio.get_event_loop()


async def send_and_get_transaction(client, data, sender_pk):
    if not data.get('nonce'):
        data['nonce'] = await client.eth_getTransactionCount(get_address(sender_pk), 'pending')

    tx = MTransaction(**data)
    signed_tx = tx.sign(sender_pk)

    tx_id = await client.eth_sendRawTransaction(to_hex(signed_tx.raw))

    print("Transaction hash: %s" % tx_id)

    assert tx_id == to_hex(signed_tx.hash), 'Hashes are not equal'

    tx_data = await client.eth_getTransactionByHash(tx_id)
    print("Transaction data:")
    pprint.pprint(tx_data)

    print("Waiting until mined..")
    tx_data = await get_tx_until_mined(client, tx_id)

    print("Transaction data mined:")
    pprint.pprint(tx_data)

    return tx_data


async def main():
    client = await aioethereum.create_ethereum_client(settings.NODE_URL, loop=loop)

    # prepare payload data
    data = {
        'to': '0xde5e2aab4a04f5c3b6b39fde028dc592bb7b902b',
        'data': b'Empty msg',
        'startgas': 22000,
        'gasprice': 0,
        'value': 2
    }
    await send_and_get_transaction(client, data, sender_pk=settings.SENDER_PK)


if __name__ == '__main__':
    loop.run_until_complete(main())
