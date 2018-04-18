import asyncio

import aioethereum

import settings
from utils import (
    get_contract_translator, create_contract_function_payload,
    get_address, to_hex,
)
from m3_send_offline_transaction import send_and_get_transaction

loop = asyncio.get_event_loop()


async def call_contract_method(client, ct, contract_address, method, args=None, *, sender_pk):
    if args is None:
        args = []

    response = await client.eth_call(get_address(sender_pk), contract_address,
                                     data=to_hex(ct.encode_function_call(method, args)))

    try:
        result = ct.decode_function_result(method, response)[0]
    except IndexError:
        raise ValueError('Incorrect result for decoding')
    print("Method '%s' result: %s" % (method, result))
    return result


async def main():
    client = await aioethereum.create_ethereum_client(settings.NODE_URL, loop=loop)
    ct = get_contract_translator(settings.ACTIVATOR_ABI)

    # prepare payload data
    data = create_contract_function_payload(ct, 'reg', [b'hello blockchain'], settings.ACTIVATOR_ADDRESS)

    await send_and_get_transaction(client, data, sender_pk=settings.SENDER_PK)
    await asyncio.gather(
        call_contract_method(client, ct, data['to'], 'userExist', sender_pk=settings.SENDER_PK),
        call_contract_method(client, ct, data['to'], 'getNote', sender_pk=settings.SENDER_PK)
    )


if __name__ == '__main__':
    loop.run_until_complete(main())
