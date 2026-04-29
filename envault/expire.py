"""Expiry policies for vault keys — set an absolute expiry date and check/purge expired keys."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from envault.vault import load_vault, save_vault


class ExpireError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _expire_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".expire.json")


def _load(vault_file: str) -> dict:
    p = _expire_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_file: str, data: dict) -> None:
    _expire_path(vault_file).write_text(json.dumps(data, indent=2))


def set_expiry(vault_file: str, password: str, key: str, expires_at: datetime) -> None:
    """Set an absolute expiry datetime (UTC) for *key*."""
    vault = load_vault(vault_file, password)
    if key not in vault:
        raise ExpireError(f"Key '{key}' not found in vault")
    data = _load(vault_file)
    data[key] = expires_at.astimezone(timezone.utc).isoformat()
    _save(vault_file, data)


def get_expiry(vault_file: str, key: str) -> datetime | None:
    """Return the expiry datetime for *key*, or None if not set."""
    data = _load(vault_file)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(vault_file: str, key: str) -> bool:
    """Return True if *key* has passed its expiry date."""
    expiry = get_expiry(vault_file, key)
    if expiry is None:
        return False
    return _now() >= expiry


def remove_expiry(vault_file: str, key: str) -> None:
    """Remove the expiry policy for *key* (no-op if not set)."""
    data = _load(vault_file)
    data.pop(key, None)
    _save(vault_file, data)


def purge_expired(vault_file: str, password: str) -> list[str]:
    """Delete all vault keys that have passed their expiry date. Returns list of purged keys."""
    data = _load(vault_file)
    vault = load_vault(vault_file, password)
    purged: list[str] = []
    now = _now()
    for key, raw in list(data.items()):
        if datetime.fromisoformat(raw) <= now and key in vault:
            del vault[key]
            del data[key]
            purged.append(key)
    save_vault(vault_file, password, vault)
    _save(vault_file, data)
    return purged
