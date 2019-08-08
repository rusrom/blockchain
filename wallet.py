from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# need for SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

# Necessary for signing
# from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from base64 import b64decode

PASSWORD = 'In_Crypto_We_Trust'
MESSAGE = 'HELLO_w_o_rl_d'


class Wallet:
    def __init__(self, hosting_node_port):
        self.private_key = None
        self.public_key = None
        self.hosting_node_port = hosting_node_port

    def generate_keys(self):
        '''Generate Private and Public keys'''

        # Generate PRIVATE KEY as RSAPrivateKey Object
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate PUBLIC KEY as RSAPublicKey Object
        self.public_key = self.private_key.public_key()

        return {
            'address': self.address,
            'message': 'New wallet created'
        }

    def load_keys(self):
        '''Load public and private keys from file in PEM format'''
        # TODO: Add try/except for files with keys not found
        # Load encrypted private key
        with open(f'data/keys/{self.hosting_node_port}-private_key_encrypted.pem', 'rb') as private_encypted_file:
            private_key = serialization.load_pem_private_key(
                private_encypted_file.read(),
                password=PASSWORD.encode(),
                backend=default_backend()
            )
        self.private_key = private_key

        # Load public key
        with open(f'data/keys/{self.hosting_node_port}-public_key.pem', 'rb') as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        self.public_key = public_key

        return {
            'address': self.address,
            'message': 'Wallet loaded'
        }

    def public_key_to_string(self):
        '''Return public key string from RSAPublicKey Object'''
        public_key_strings = self.public_key_pem.decode().splitlines()
        public_key_string = ''.join(public_key_strings[1:-1])
        return public_key_string

    def public_key_from_string(self, public_key_string):
        '''Return RSAPublicKey Object from public key string'''
        der_data = b64decode(public_key_string)
        public_key_obj = serialization.load_der_public_key(der_data, backend=default_backend())
        return public_key_obj

    @property
    def private_key_pem(self):
        '''Serialize private key in PEM format'''

        # Serialize PRIVATE KEY to bytestring
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

    @property
    def private_key_encrypted_pem(self):
        '''Serialize encryted privvate key in PEM format'''

        # Serialize PRIVATE KEY WITH ENCRYPTION to bytestring
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(PASSWORD.encode())
        )

    @property
    def public_key_pem(self):
        '''Serialize public key to string in PEM format'''

        # Serialize PUBLIC KEY to bytestring
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @property
    def address(self):
        '''Client wallet address in Blockchain'''

        public_key_strings = self.public_key_pem.decode().splitlines()
        public_key_string = ''.join(public_key_strings[1:-1])

        # SHA256 from publick key string
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(public_key_string.encode())
        public_key_sha256 = digest.finalize()
        return public_key_sha256.hex()

    def save_keys(self):
        # Save serialized private key to .pem file
        with open(f'data/keys/{self.hosting_node_port}-private_key.pem', 'wb') as f:
            f.write(self.private_key_pem)

        # Save serialized encrypted private key to .pem file
        with open(f'data/keys/{self.hosting_node_port}-private_key_encrypted.pem', 'wb') as f:
            f.write(self.private_key_encrypted_pem)

        # Save serialized public key to .pem file
        with open(f'data/keys/{self.hosting_node_port}-public_key.pem', 'wb') as f:
            f.write(self.public_key_pem)

    def sign_transaction(self, message_string):
        signature = self.private_key.sign(
            message_string.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # Return the hexadecimal representation of the binary hex data.
        return signature.hex()

    @classmethod
    def check_signature(cls, public_key_string, message_string, signature_string):
        # Get byte string from message string
        message = message_string.encode()

        # Return the binary hex data represented by the hexadecimal string.
        signature = bytes.fromhex(signature_string)

        # Return RSAPublicKey object from public key string
        der_data = b64decode(public_key_string)
        public_key_obj = serialization.load_der_public_key(der_data, backend=default_backend())

        try:
            public_key_obj.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print('Tansaction signature OK!')
            return True
        except InvalidSignature:
            print('[CRITICAL ERROR] Signature failed')
            return False


# if __name__ == "__main__":
#     transaction_signature = 'ae3a92dfb6ce1a5769d1ee66a7b363fd0506d35577a9a5ef40dae0339be302ce14787c8f4cd4d34087f0c1c13c0a28839aae4e06b6e5ac02a5a1c6a28afa4a1d1fc7971c91fdfb0bf731b5faee2f0bf28869341a143f45dc26ec9ad3160d921ee46b88dac1344dbb438714b47962728ce286da8ea1db79f25047d251eb0a1da95e31382de2993a4ebbb15fc041b60d7f8e9a3a5cb590905dc18e5290318e42ba3294b1cea7bb5761cf1eb2c5ffd7b4e1dad6a1b6a1748fef5a73be7e7947b8318f0c808a804e58d39f67b498a31dd38a6b55a5877bbd2cd0275a9f85ce2539334012aebfef5cd6a3576b391219364b72a4f965f7404f73fa134dc2ced0efaa8a'

#     wallet = Wallet(5000)
#     wallet.load_keys()
#     # print(wallet.public_key)
#     # print(wallet.address)
#     # print(wallet.public_key_pem)
#     # print(wallet.public_key_pem.decode())

#     # print('Public key string')
#     # pub_key_str = wallet.public_key_to_string()
#     # print(pub_key_str)
#     pub_key_str_copy = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3CPXhKOGh6UXbcMD4tJceGVAeNZkdCvwn8ZhVol9+S5zkaEFXxu1nMQQqoHisKhdGowFMqwBbTU7a1yibSEeaiRpSAtLrf9ggedAZHq7UbohaRXaLaqF2xub4WogJMDjts+y+NbgyE31JbNlF0AXjuBc2cQzjeEI8PvbpfE3SGH68jZcKNl9xr0LgIEp0XExtTqBA/NUL1IFfTH7RWr/SZJfMwaB+YL4rDHG0RMQBg6mDwY0Z6NSkdyfxwwEmINJv6oeesAFeomhgsk0iUzbIrqtYwT3zskU+S6hCX65jp/JoxaNXfgn3r7C7wOsExqxq/Bm2nrldDfQ/E9U+mm6OQIDAQAB'

#     # print('\nFrom string to public object')
#     # pub_key_obj = wallet.public_key_from_string(pub_key_str_copy)
#     # print('Result')
#     # print(pub_key_obj)



#     # print('\nSigature\n')
#     message_string = 'Some text to sign with private key'
#     # signature_string = wallet.sign_transaction(message_string)
#     # print(signature_string)
#     print('\nCheck signature\n')
#     res = Wallet.check_signature(pub_key_str_copy, message_string, transaction_signature)
#     print(res)


# #     pub_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApLqG4Yf8OLwWO7gqrkHBEAH5InilRFN8QmZcECIE4jBpHKQDfCG0HUkLieFdPiHTq4ksNa6mAtuyY29La3GpkCXGOfBRtQWA7GqU2GbZIqIVxjE3BVE94kDjbifKv87IpRbrKVIJPf7C8n+MTWHfwllU3njPB8bUwEWzlERMlSn2S6JYZh5kSBFdhsQe8TDX9MbM4YE9ZvE5B+kRwoYJQHSE+8xWc8peK7/ESUuLi2tuFCGGEd3YcdMvHxxPOzV8Wcj52YhHKRGERPlNGvr6Z16UJOI/g1Pio/JKONUmVQnuzkfe0LiGS2H915S9z3mlbRGroB9+GrATfd7AEtcxFwIDAQAB'

# #     publ_k = wallet.public_key_from_string(pub_key)
# #     print(publ_k)
# #     print(dir(publ_k))

# #     # Serialize PUBLIC KEY to bytestring
# #     e = publ_k.public_bytes(
# #         encoding=serialization.Encoding.PEM,
# #         format=serialization.PublicFormat.SubjectPublicKeyInfo
# #     )

# #     print(e)
