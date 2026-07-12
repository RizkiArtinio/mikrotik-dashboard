from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class EncryptionError(Exception):
    pass


@lru_cache
def _fernet() -> Fernet:
    if not settings.fernet_key:
        raise EncryptionError(
            "FERNET_KEY is not set. Generate one with "
            "`python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"` "
            "and set it in .env before storing router credentials."
        )
    return Fernet(settings.fernet_key.encode())


def encrypt_secret(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise EncryptionError("Failed to decrypt stored secret — FERNET_KEY may have changed.") from exc
