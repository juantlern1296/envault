"""Retention policy: automatically delete vars after N days of inactivity."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault, delete_var


class RetentionError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _retention_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".retention.json")


def _load(vault_path: str) -> dict:
    p = _retention_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _retention_path(vault_path).write_text(json.dumps(data, indent=2))


def set_retention(vault_path: str, password: str, key: str, days: int) -> None:
    """Set a retention policy (in days) for a vault key."""
    if days <= 0:
        raise RetentionError("days must be a positive integer")
    vault = load_vault(vault_path, password)
    if key not in vault:
        raise RetentionError(f"key '{key}' not found in vault")
    data = _load(vault_path)
    data[key] = {
        "days": days,
        "last_accessed": _now().isoformat(),
    }
    _save(vault_path, data)


def get_retention(vault_path: str, key: str) -> Optional[dict]:
    """Return retention info for a key, or None if not set."""
    return _load(vault_path).get(key)


def touch_key(vault_path: str, key: str) -> None:
    """Update the last_accessed timestamp for a key."""
    data = _load(vault_path)
    if key in data:
        data[key]["last_accessed"] = _now().isoformat()
        _save(vault_path, data)


def purge_stale(vault_path: str, password: str) -> list[str]:
    """Delete all vars whose retention period has elapsed. Returns list of deleted keys."""
    data = _load(vault_path)
    now = _now()
    deleted = []
    for key, info in list(data.items()):
        last = datetime.fromisoformat(info["last_accessed"])
        age_days = (now - last).total_seconds() / 86400
        if age_days >= info["days"]:
            try:
                delete_var(vault_path, password, key)
            except Exception:
                pass
            del data[key]
            deleted.append(key)
    _save(vault_path, data)
    return deleted


def remove_retention(vault_path: str, key: str) -> None:
    """Remove retention policy for a key."""
    data = _load(vault_path)
    if key not in data:
        raise RetentionError(f"no retention policy set for '{key}'")
    del data[key]
    _save(vault_path, data)
