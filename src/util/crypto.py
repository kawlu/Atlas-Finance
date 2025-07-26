import base64
import hashlib
from cryptography.fernet import Fernet

class CryptoManager:
    _SENHA = b"Lx^6Z!98@r2$Qv#Po123&"

    @staticmethod
    def _get_chave():
        hash_senha = hashlib.sha256(CryptoManager._SENHA).digest()
        return base64.urlsafe_b64encode(hash_senha)

    @staticmethod
    def criptografar(texto: str) -> bytes:
        chave = CryptoManager._get_chave()
        f = Fernet(chave)
        return f.encrypt(texto.encode())

    @staticmethod
    def descriptografar(token: bytes) -> str:
        chave = CryptoManager._get_chave()
        f = Fernet(chave)
        return f.decrypt(token).decode()