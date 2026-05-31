import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: str) -> bytes:
    """Dérive une clé AES-256 à partir d'un mot de passe"""
    salt = b'\x00' * 16 # Salt fixe pour la simulation (pour pouvoir déchiffrer)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # 32 octets = 256 bits
        salt=salt,
        iterations=600000,
    )
    return kdf.derive(password.encode())

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Chiffrement AES-GCM : Nonce (12 bytes) + Ciphertext"""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext # On stocke le nonce au début du fichier

def decrypt_data(data: bytes, key: bytes) -> bytes:
    """Déchiffrement AES-GCM"""
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)
