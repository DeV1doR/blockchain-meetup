import asyncio
import binascii
import re

from ethereum import utils

from m4_execute_contract_method import (
    send_and_get_transaction, create_contract_function_payload, ct, to_hex
)

loop = asyncio.get_event_loop()


# store decrypted pk
SENDER_PK = 'ab17ca9b5300e0a569f4f8e077eae1581c965daf0e19d5df1763b23a1c1605a2'
# or use some other keystorage service

# contract addres for execution
ACTIVATOR_ADDRESS = '0x0716416a52dbb014be680fd6f0748717d3668f73'


def parse_logs(tx_result):
    for log in tx_result['logs']:
        decoded = ct.decode_event([int(log['topics'][0], 16)],
                                  utils.remove_0x_head(log['data']))
        yield decoded['_event_type'], decoded['']


def low_level_parse_logs(tx_result, events=None):
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
    # prepare payload data
    data = create_contract_function_payload('reg', [b'hello blockchain'])
    tx_result = await send_and_get_transaction(data, sender_pk=SENDER_PK)
    print('H=============')
    print_logs(parse_logs(tx_result))
    print('L=============')
    print_logs(low_level_parse_logs(tx_result))


if __name__ == '__main__':
    loop.run_until_complete(main())
