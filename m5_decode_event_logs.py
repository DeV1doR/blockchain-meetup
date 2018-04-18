import asyncio
import binascii
import re

import aioethereum
from ethereum import utils

import settings
from utils import create_contract_function_payload, to_hex, get_contract_translator
from m3_send_offline_transaction import send_and_get_transaction

loop = asyncio.get_event_loop()


def parse_logs(ct, tx_result):
    for log in tx_result['logs']:
        decoded = ct.decode_event([int(log['topics'][0], 16)],
                                  utils.remove_0x_head(log['data']))
        yield decoded['_event_type'], decoded['']


def low_level_parse_logs(ct, tx_result, events=None):
    if events is None:
        events = ['Error(bytes32)', 'Success(bytes32)']

    sha3_events = {to_hex(utils.sha3(event)): re.search('.*?(?=\()', event).group(0).encode('utf-8')
                   for event in events}
    for log in tx_result['logs']:
        if log['topics'][0] in sha3_events:
            yield sha3_events[log['topics'][0]], utils.remove_0x_head(log['data']).rstrip('0')


def print_logs(logs):
    for log in logs:
        event_name, value = log[0], log[1]
        print('Event: %s, Value: %s' %
              (event_name.decode('utf-8'), binascii.unhexlify(value).decode('utf-8')))


async def main():
    client = await aioethereum.create_ethereum_client(settings.NODE_URL, loop=loop)
    ct = get_contract_translator(settings.ACTIVATOR_ABI)
    # prepare payload data
    data = create_contract_function_payload(ct, 'reg', [b'hello blockchain'], settings.ACTIVATOR_ADDRESS)
    tx_result = await send_and_get_transaction(client, data, sender_pk=settings.SENDER_PK)

    print('H=============')
    print_logs(parse_logs(ct, tx_result))
    print('L=============')
    print_logs(low_level_parse_logs(ct, tx_result))


if __name__ == '__main__':
    loop.run_until_complete(main())
