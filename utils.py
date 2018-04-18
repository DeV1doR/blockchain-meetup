import binascii
import asyncio

import rlp
from ethereum import utils
from ethereum.transactions import Transaction
from ethereum.abi import ContractTranslator


class MTransaction(Transaction):

    @property
    def raw(self):
        return rlp.encode(self)

    @property
    def hash(self):
        return utils.sha3(self.raw)


def get_contract_translator(abi):
    return ContractTranslator(abi)


def to_hex(b):
    return '0x{0}'.format(binascii.hexlify(b).decode('utf-8'))


def get_address(pk):
    return to_hex(utils.privtoaddr(pk))


def hex_to_str(hx):
    return binascii.unhexlify(utils.remove_0x_head(hx)).decode('utf-8')


def join_vrs(v, r, s):
    return '0x' + utils.remove_0x_head(hex(r)) + utils.remove_0x_head(hex(s)) + utils.remove_0x_head(hex(v))


def create_contract_function_payload(ct, method, args, contract_address):
    return {
        'to': contract_address,
        'data': ct.encode_function_call(method, args),
        'startgas': 500000,
        'gasprice': 0,
        'value': 0
    }


async def get_tx_until_mined(client, tx_id, ttl=30):
    while ttl:
        ttl -= 1
        tx_data = await client.eth_getTransactionReceipt(tx_id)
        if tx_data:
            return tx_data
        await asyncio.sleep(1)
    raise ValueError('Transaction still not mined')
