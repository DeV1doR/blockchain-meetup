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


# store decrypted pk
SENDER_PK = 'ab17ca9b5300e0a569f4f8e077eae1581c965daf0e19d5df1763b23a1c1605a2'
# or use some other keystorage service

# contract ABI
ABI = json.loads('[{"constant":false,"inputs":[],"name":"unreg","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"note","type":"bytes32"}],"name":"reg","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"userExist","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getNote","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_limit","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"","type":"bytes32"}],"name":"Error","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"","type":"bytes32"}],"name":"Success","type":"event"}]')
ct = ContractTranslator(ABI)

# contract addres for execution
ACTIVATOR_ADDRESS = '0x0716416a52dbb014be680fd6f0748717d3668f73'


def to_hex(b):
    return '0x{0}'.format(binascii.hexlify(b).decode('utf-8'))


def get_address(pk):
    return to_hex(utils.privtoaddr(pk))


def hex_to_str(hx):
    return binascii.unhexlify(utils.remove_0x_head(hx)).decode('utf-8')


def create_contract_function_payload(method, args, contract_address=ACTIVATOR_ADDRESS):
    return {
        'to': contract_address,
        'data': ct.encode_function_call(method, args),
        'startgas': 500000,
        'gasprice': 0,
        'value': 0
    }


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

    await asyncio.gather(
        call_contract_method(data['to'], 'userExist', sender_pk=sender_pk),
        call_contract_method(data['to'], 'getNote', sender_pk=sender_pk)
    )
    return tx_data


async def call_contract_method(contract_address, method, args=None, *, sender_pk):
    if args is None:
        args = []

    client = await aioethereum.create_ethereum_client(
        'http://localhost:8545', loop=loop)
    response = await client.eth_call(get_address(sender_pk), contract_address,
                                     data=to_hex(ct.encode_function_call(method, args)))

    try:
        result = ct.decode_function_result(method, response)[0]
    except IndexError:
        raise ValueError('Incorrect result for decoding')
    print("Method '%s' result: %s" % (method, result))
    return result


async def get_tx_until_mined(client, tx_id, ttl=30):
    while ttl:
        ttl -= 1
        tx_data = await client.eth_getTransactionReceipt(tx_id)
        if tx_data:
            return tx_data
        await asyncio.sleep(1)
    raise ValueError('Transaction still not mined')


if __name__ == '__main__':
    # prepare payload data
    data = create_contract_function_payload('reg', [b'hello blockchain'])
    loop.run_until_complete(send_and_get_transaction(data, sender_pk=SENDER_PK))
