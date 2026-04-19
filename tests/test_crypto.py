"""Tests for envault.crypto encryption/decryption."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/db\nAPI_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_decrypt_roundtrip():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == PLAINTEXT


def test_encrypt_produces_different_ciphertexts():
    """Each encryption should produce a unique ciphertext (random salt+nonce)."""
    enc1 = encrypt(PLAINTEXT, PASSWORD)
    enc2 = encrypt(PLAINTEXT, PASSWORD)
    assert enc1 != enc2


def test_decrypt_wrong_password_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, "wrong-password")


def test_decrypt_corrupted_data_raises():
    with pytest.raises(ValueError):
        decrypt("notvalidbase64!!!", PASSWORD)


def test_decrypt_truncated_blob_raises():
    import base64
    short_blob = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="blob too short"):
        decrypt(short_blob, PASSWORD)


def test_empty_plaintext_roundtrip():
    encrypted = encrypt("", PASSWORD)
    assert decrypt(encrypted, PASSWORD) == ""


def test_unicode_plaintext_roundtrip():
    unicode_text = "SECRET=caf\u00e9-\u4e2d\u6587-\U0001f511"
    encrypted = encrypt(unicode_text, PASSWORD)
    assert decrypt(encrypted, PASSWORD) == unicode_text
