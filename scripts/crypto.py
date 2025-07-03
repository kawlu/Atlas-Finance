from cryptography.fernet import Fernet
import base64
import hashlib

def get_chave():
    senha = b"Lx^6Z!98@r2$Qv#Po123&"
    hash_senha = hashlib.sha256(senha).digest()
    chave = base64.urlsafe_b64encode(hash_senha)
    return chave

def criptografar(texto):
    chave = get_chave()
    f = Fernet(chave)
    return f.encrypt(texto.encode())

def descriptografar(token):
    chave = get_chave()
    f = Fernet(chave)
    return f.decrypt(token).decode()