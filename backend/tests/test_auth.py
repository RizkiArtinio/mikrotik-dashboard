from app.core.crypto import decrypt_secret, encrypt_secret
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_jwt_roundtrip():
    token = create_access_token(subject="admin@example.com", role="super_admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "admin@example.com"
    assert payload["role"] == "super_admin"


def test_router_password_encryption_roundtrip():
    ciphertext = encrypt_secret("my-router-password")
    assert ciphertext != "my-router-password"
    assert decrypt_secret(ciphertext) == "my-router-password"
