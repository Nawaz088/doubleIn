import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings

_key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
_key = base64.urlsafe_b64encode(_key_bytes)
_fernet = Fernet(_key)


def encrypt_token(token: str) -> str:
    return _fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    return _fernet.decrypt(encrypted.encode()).decode()
