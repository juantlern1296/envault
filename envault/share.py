"""Secure variable sharing between users via encrypted share tokens."""

import base64
import json
from typing import Optional

from envault.crypto import derive_key, encrypt, decrypt
from envault.vault import load_vault


def create_share_token(vault_path: str, password: str, key: str, share_password: str) -> str:
    """Create a share token for a single variable encrypted with share_password."""
    vault = load_vault(vault_path, password)
    if key not in vault:
        raise KeyError(f"Variable '{key}' not found in vault.")
    payload = json.dumps({"key": key, "value": vault[key]})
    token_bytes = encrypt(payload, share_password)
    return base64.urlsafe_b64encode(token_bytes.encode()).decode()


def read_share_token(token: str, share_password: str) -> dict:
    """Decode and decrypt a share token, returning {key, value}."""
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        payload = decrypt(raw, share_password)
        return json.loads(payload)
    except Exception as exc:
        raise ValueError("Invalid token or wrong share password.") from exc


def import_share_token(vault_path: str, password: str, token: str, share_password: str, override_key: Optional[str] = None) -> str:
    """Import a shared variable into the local vault. Returns the key name stored."""
    from envault.vault import set_var
    data = read_share_token(token, share_password)
    key = override_key or data["key"]
    set_var(vault_path, password, key, data["value"])
    return key
