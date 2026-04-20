"""TTL (time-to-live) support for vault variables."""

from datetime import datetime, timezone, timedelta
from envault.vault import load_vault, save_vault


def _now() -> datetime:
    return datetime.now(timezone.utc)


def set_ttl(vault_path: str, password: str, key: str, seconds: int) -> None:
    """Set expiry on an existing variable."""
    data = load_vault(vault_path, password)
    if key not in data:
        raise KeyError(f"Variable '{key}' not found")
    expires_at = (_now() + timedelta(seconds=seconds)).isoformat()
    meta = data.get("__ttl__", {})
    meta[key] = expires_at
    data["__ttl__"] = meta
    save_vault(vault_path, password, data)


def get_ttl(vault_path: str, password: str, key: str) -> str | None:
    """Return ISO expiry string for key, or None if no TTL set."""
    data = load_vault(vault_path, password)
    return data.get("__ttl__", {}).get(key)


def is_expired(vault_path: str, password: str, key: str) -> bool:
    """Return True if the variable has expired."""
    expiry = get_ttl(vault_path, password, key)
    if expiry is None:
        return False
    return _now() > datetime.fromisoformat(expiry)


def purge_expired(vault_path: str, password: str) -> list[str]:
    """Delete all expired variables and return their keys."""
    data = load_vault(vault_path, password)
    meta = data.get("__ttl__", {})
    removed = []
    for key, expiry in list(meta.items()):
        if _now() > datetime.fromisoformat(expiry):
            data.pop(key, None)
            meta.pop(key)
            removed.append(key)
    data["__ttl__"] = meta
    save_vault(vault_path, password, data)
    return removed
