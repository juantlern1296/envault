"""Vault file management — read/write encrypted .envault files."""

import json
import os
from pathlib import Path

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"


def load_vault(password: str, vault_path: str = DEFAULT_VAULT_FILE) -> dict:
    """Load and decrypt the vault file, returning a dict of env vars."""
    path = Path(vault_path)
    if not path.exists():
        return {}

    ciphertext = path.read_text().strip()
    if not ciphertext:
        return {}

    plaintext = decrypt(ciphertext, password)
    return json.loads(plaintext)


def save_vault(data: dict, password: str, vault_path: str = DEFAULT_VAULT_FILE) -> None:
    """Encrypt and save env vars dict to the vault file."""
    plaintext = json.dumps(data)
    ciphertext = encrypt(plaintext, password)
    Path(vault_path).write_text(ciphertext + "\n")


def set_var(key: str, value: str, password: str, vault_path: str = DEFAULT_VAULT_FILE) -> None:
    """Add or update a single env var in the vault."""
    data = load_vault(password, vault_path)
    data[key] = value
    save_vault(data, password, vault_path)


def get_var(key: str, password: str, vault_path: str = DEFAULT_VAULT_FILE) -> str | None:
    """Retrieve a single env var from the vault."""
    data = load_vault(password, vault_path)
    return data.get(key)


def delete_var(key: str, password: str, vault_path: str = DEFAULT_VAULT_FILE) -> bool:
    """Remove a var from the vault. Returns True if it existed."""
    data = load_vault(password, vault_path)
    if key not in data:
        return False
    del data[key]
    save_vault(data, password, vault_path)
    return True


def list_vars(password: str, vault_path: str = DEFAULT_VAULT_FILE) -> dict:
    """Return all env vars stored in the vault."""
    return load_vault(password, vault_path)
