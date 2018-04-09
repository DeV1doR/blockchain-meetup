import binascii

import sha3
from ecdsa import SigningKey, SECP256k1


def generate_private_key():
    priv = SigningKey.generate(curve=SECP256k1)
    return binascii.hexlify(priv.to_string()).decode('utf-8')


def private_to_public_key(priv_key, fmt='uncompressed'):
    if isinstance(priv_key, (str, bytes)):
        priv_key = binascii.unhexlify(priv_key)
    priv = SigningKey.from_string(priv_key, curve=SECP256k1)
    pub = priv.get_verifying_key()
    pub_key = binascii.hexlify(pub.to_string()).decode('utf-8')
    if fmt == 'uncompressed':
        return pub_key
    elif fmt == 'compressed':
        return pub_key[:64]
    raise ValueError('Invalid "fmt"')


def public_to_address(pub_key):
    if isinstance(pub_key, (str, bytes)):
        pub_key = binascii.unhexlify(pub_key)
    return sha3.keccak_256(pub_key).hexdigest()[-40:]


if __name__ == '__main__':
    private_key = generate_private_key()
    print('Generated private key (hex): 0x%s' % private_key, end='\n\n')

    public_key = private_to_public_key(private_key)
    print('Derived public key (hex uncompressed): 0x04%s' % public_key, end='\n\n')

    ethereum_address = public_to_address(public_key)
    print('Derived address (hex): 0x%s' % ethereum_address, end='\n\n')
