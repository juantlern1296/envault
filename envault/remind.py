"""Reminders: flag vault keys for review after a given number of days."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from envault.vault import load_vault


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _reminders_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".reminders.json")


def _load(vault_file: str) -> dict:
    p = _reminders_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_file: str, data: dict) -> None:
    _reminders_path(vault_file).write_text(json.dumps(data, indent=2))


def set_reminder(vault_file: str, password: str, key: str, days: int) -> datetime:
    """Schedule a reminder for *key* in *days* days from now."""
    vault = load_vault(vault_file, password)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault")
    if days <= 0:
        raise ValueError("days must be a positive integer")
    due = _now() + timedelta(days=days)
    data = _load(vault_file)
    data[key] = due.isoformat()
    _save(vault_file, data)
    return due


def get_reminder(vault_file: str, key: str) -> Optional[datetime]:
    """Return the due datetime for *key*, or None if not set."""
    data = _load(vault_file)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def remove_reminder(vault_file: str, key: str) -> None:
    """Remove the reminder for *key*. Raises KeyError if not set."""
    data = _load(vault_file)
    if key not in data:
        raise KeyError(f"No reminder set for '{key}'")
    del data[key]
    _save(vault_file, data)


def due_reminders(vault_file: str) -> list[tuple[str, datetime]]:
    """Return all (key, due) pairs whose due date is now or in the past."""
    data = _load(vault_file)
    now = _now()
    result = []
    for key, raw in data.items():
        due = datetime.fromisoformat(raw)
        if due <= now:
            result.append((key, due))
    result.sort(key=lambda t: t[1])
    return result
