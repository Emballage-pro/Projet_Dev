import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_strong_key(password: str) -> bytes:
    """Génère une clé dérivée via PBKDF2"""
    password_bytes = password.encode('utf-8')
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password_bytes))

def encrypt_data(data: bytes, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.encrypt(data)

def decrypt_data(data: bytes, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.decrypt(data)
