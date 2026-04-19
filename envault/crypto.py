"""Encryption and decryption utilities for envault using AES-GCM."""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


NONCE_SIZE = 12  # 96-bit nonce for AES-GCM
KEY_SIZE = 32   # 256-bit key


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a password using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=260_000,
        dklen=KEY_SIZE,
    )


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt plaintext with a password. Returns a base64-encoded blob.

    Format: base64(salt[16] + nonce[12] + ciphertext)
    """
    salt = os.urandom(16)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    blob = salt + nonce + ciphertext
    return base64.b64encode(blob).decode("utf-8")


def decrypt(encoded: str, password: str) -> str:
    """Decrypt a base64-encoded blob with a password. Returns plaintext.

    Raises ValueError on bad password or corrupted data.
    """
    try:
        blob = base64.b64decode(encoded.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid encrypted data: not valid base64.") from exc

    if len(blob) < 16 + NONCE_SIZE + 16:  # salt + nonce + min GCM tag
        raise ValueError("Invalid encrypted data: blob too short.")

    salt = blob[:16]
    nonce = blob[16:16 + NONCE_SIZE]
    ciphertext = blob[16 + NONCE_SIZE:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed: wrong password or corrupted data.") from exc

    return plaintext.decode("utf-8")
