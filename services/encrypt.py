from Crypto.Cipher import AES

from config import SESSION_SECRET_KEY, SESSION_SECRET_NONCE


class EncryptService:
    def __init__(self, key: str, nonce: str):
        self.key = key.encode()
        self.nonce = nonce.encode()

    def encrypt(self, s: str) -> str:
        if not self.key or not self.nonce:
            return s
        cipher = self.get_cipher()
        return cipher.encrypt(s.encode()).hex()

    def decrypt(self, s: str) -> str:
        if not self.key or not self.nonce:
            return s
        cipher = self.get_cipher()
        return cipher.decrypt(bytes.fromhex(s)).decode()

    def get_cipher(self):
        return AES.new(self.key, AES.MODE_GCM, nonce=self.nonce)


def get_encrypt_service() -> EncryptService:
    return EncryptService(SESSION_SECRET_KEY, SESSION_SECRET_NONCE)
