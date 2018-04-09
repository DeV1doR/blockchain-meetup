import binascii
import asyncio

import pprint
import aioethereum

loop = asyncio.get_event_loop()


async def unlock_send_and_get_transaction(data, pswd):
    client = await aioethereum.create_ethereum_client(
        'http://localhost:8545', loop=loop)

    # 1. Unlock account
    await client.personal_unlockAccount(data['from_'], pswd)

    # 2. Make send transaction to the node
    tx_id = await client.eth_sendTransaction(**data)

    # 3. Lock back account
    await client.personal_lockAccount(data['from_'])

    print("Transaction hash: %s" % tx_id)

    print("Waiting until mined..")
    tx_data = await get_tx_until_mined(client, tx_id)

    print("Transaction data:")
    pprint.pprint(tx_data)


async def get_tx_until_mined(client, tx_id):
    tx_data = await client.eth_getTransactionReceipt(tx_id)
    if not tx_data:
        await asyncio.sleep(1)
        return await get_tx_until_mined(client, tx_id)
    return tx_data


if __name__ == '__main__':
    # prepare payload data
    data = {
        'from_': '0xaacfd449690e7581f75b89861a76df37f88ce4d8',
        'to': '0x1e6d3e3474705373e6fe211823dffd0e512ec531',
        'data': '0x' + binascii.hexlify(b'Empty msg').decode('utf-8'),
        'gas': 22000,
        'gas_price': 0,
        'value': 0.1
    }
    # retrieve a password for unlock mechanizm
    with open('./node_db/pswd.txt', 'r') as reader:
        pswd = reader.read()

    loop.run_until_complete(unlock_send_and_get_transaction(data, pswd))
