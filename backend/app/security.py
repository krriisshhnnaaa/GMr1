from cryptography.fernet import Fernet
from .config import get_settings
import base64
import hashlib


def _fernet() -> Fernet:
    key = get_settings().encryption_key
    if not key:
        key = base64.urlsafe_b64encode(hashlib.sha256(get_settings().app_secret.encode()).digest()).decode()
    return Fernet(key.encode())


def encrypt_secret(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()
