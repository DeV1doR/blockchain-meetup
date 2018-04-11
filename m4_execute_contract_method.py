import binascii
import asyncio
import json

import rlp
import pprint
import aioethereum
from ethereum import utils
from ethereum.transactions import Transaction
from ethereum.abi import ContractTranslator

loop = asyncio.get_event_loop()


def to_hex(b):
    return '0x{0}'.format(binascii.hexlify(b).decode('utf-8'))


def get_address(pk):
    return to_hex(utils.privtoaddr(pk))


class MTransaction(Transaction):

    @property
    def raw(self):
        return rlp.encode(self)

    @property
    def hash(self):
        return utils.sha3(self.raw)


async def send_and_get_transaction(data, sender_pk):
    client = await aioethereum.create_ethereum_client(
        'http://localhost:8545', loop=loop)

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


async def get_tx_until_mined(client, tx_id):
    tx_data = await client.eth_getTransactionReceipt(tx_id)
    if not tx_data:
        await asyncio.sleep(1)
        return await get_tx_until_mined(client, tx_id)
    return tx_data


if __name__ == '__main__':
    # store decrypted pk
    SENDER_PK = 'ab17ca9b5300e0a569f4f8e077eae1581c965daf0e19d5df1763b23a1c1605a2'
    # or use own keystorage service

    # contract ABI
    ABI = json.loads('[{"constant":false,"inputs":[],"name":"unreg","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"note","type":"string"}],"name":"reg","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"userExist","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getNote","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_limit","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"","type":"bytes32"}],"name":"Error","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"","type":"bytes32"}],"name":"Success","type":"event"}]')
    ct = ContractTranslator(ABI)

    # prepare payload data
    data = {
        'to': '0x09102f332712a99bb0c54c6f1ba30f0a0aad9a18',
        'data': ct.encode_function_call('reg', ['hello']),
        'startgas': 500000,
        'gasprice': 0,
        'value': 0
    }
    loop.run_until_complete(send_and_get_transaction(data, SENDER_PK))
