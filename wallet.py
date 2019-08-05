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

PASSWORD = 'In_Crypto_We_Trust'
MESSAGE = 'HELLO_w_o_rl_d'


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

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
        with open("keys/private_key_encrypted.pem", "rb") as private_encypted_file:
            private_key = serialization.load_pem_private_key(
                private_encypted_file.read(),
                password=PASSWORD.encode(),
                backend=default_backend()
            )
        self.private_key = private_key

        # Load public key
        with open("keys/public_key.pem", "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        self.public_key = public_key

        return {
            'address': self.address,
            'message': 'Wallet loaded'
        }

    @property
    def private_key_pem(self):
        '''Serialize privvate key in PEM format'''

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
        '''Clien wallet address in Blockchain'''

        public_key_strings = self.public_key_pem.decode().splitlines()
        public_key_string = ''.join(public_key_strings[1:-1])

        # SHA256 from publick key string
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(public_key_string.encode())
        public_key_sha256 = digest.finalize()
        return public_key_sha256.hex()

    def save_keys(self):
        # Save serialized private key to .pem file
        with open('keys/private_key.pem', 'wb') as f:
            f.write(self.private_key_pem)

        # Save serialized encrypted private key to .pem file
        with open('keys/private_key_encrypted.pem', 'wb') as f:
            f.write(self.private_key_encrypted_pem)

        # Save serialized public key to .pem file
        with open('keys/public_key.pem', 'wb') as f:
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
    def check_signature(cls, public_key_obj, message, signature_string):
        # Return the binary hex data represented by the hexadecimal string.
        signature = bytes.fromhex(signature_string)
        try:
            public_key_obj.verify(
                signature,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print('Ytansaction signature OK!')
            return True
        except InvalidSignature:
            print('[CRITICAL ERROR] Signature failed')
            return False


if __name__ == "__main__":
    wallet = Wallet()
    wallet.generate_keys()

    # keys pem
    print(wallet.private_key_encrypted_pem)
    print(wallet.public_key_pem)
