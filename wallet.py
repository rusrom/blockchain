from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


PASSWORD = 'In_Crypto_We_Trust'


class Wallet:
    def __init__(self):
        self.generate_keys()

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

    def keys_to_string(self):
        # Serialize PRIVATE KEY WITH ENCRYPTION to bytestring
        private_key_encrypted_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(PASSWORD.encode())
        )

        # Serialize PUBLIC KEY to bytestring
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_key_encrypted_pem.decode(), public_key_pem.decode()


if __name__ == "__main__":
    wallet = Wallet()
    private_key, public_key = wallet.keys_to_string()

    print(private_key)
    print(public_key)
