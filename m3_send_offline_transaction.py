import binascii
import asyncio

import rlp
import pprint
import aioethereum
from ethereum.utils import sha3
from ethereum.transactions import Transaction

loop = asyncio.get_event_loop()


def to_hex(b):
    return '0x{0}'.format(binascii.hexlify(b).decode('utf-8'))


class MTransaction(Transaction):

    @property
    def raw(self):
        return rlp.encode(self)

    @property
    def hash(self):
        return sha3(self.raw)


async def send_and_get_transaction(sender_address, sender_pk, data):
    client = await aioethereum.create_ethereum_client(
        'http://localhost:8545', loop=loop)

    if not data.get('nonce'):
        data['nonce'] = await client.eth_getTransactionCount(sender_address, 'pending')

    tx = MTransaction(**data)
    signed_tx = tx.sign(sender_pk)

    tx_id = await client.eth_sendRawTransaction(to_hex(signed_tx.raw))

    print("Transaction hash: %s" % tx_id)

    assert tx_id == to_hex(signed_tx.hash), 'Hashes are not equal'

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
    # store decrypted
    SENDER_ADDRESS = '0xad43a314ab316cfea09d1d464a9dba1b62acf963'
    SENDER_PK = 'ab17ca9b5300e0a569f4f8e077eae1581c965daf0e19d5df1763b23a1c1605a2'
    # or use own keystorage service

    # prepare payload data
    data = {
        'to': '0xde5e2aab4a04f5c3b6b39fde028dc592bb7b902b',
        'data': b'Empty msg',
        'startgas': 22000,
        'gasprice': 0,
        'value': 2
    }
    loop.run_until_complete(send_and_get_transaction(SENDER_ADDRESS, SENDER_PK, data))
