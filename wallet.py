from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# need for SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


PASSWORD = 'In_Crypto_We_Trust'


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

    def load_keys(self):
        '''Load public and private keys from file in PEM format'''
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


if __name__ == "__main__":
    wallet = Wallet()
    wallet.generate_keys()

    print(wallet.private_key_encrypted_pem)
    print(wallet.public_key_pem)
