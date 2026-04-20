"""Variable change history tracking for envault."""
import json
import os
import time
from pathlib import Path
from typing import Optional


def _now() -> float:
    return time.time()


def _history_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".history.json")


def _load(vault_path: str) -> dict:
    hp = _history_path(vault_path)
    if not hp.exists():
        return {}
    with open(hp) as f:
        return json.load(f)


def _save(vault_path: str, data: dict) -> None:
    hp = _history_path(vault_path)
    with open(hp, "w") as f:
        json.dump(data, f, indent=2)


def record_change(vault_path: str, key: str, action: str, old_value: Optional[str] = None) -> None:
    """Record a set/delete action for a key."""
    data = _load(vault_path)
    if key not in data:
        data[key] = []
    entry = {"ts": _now(), "action": action}
    if old_value is not None:
        entry["old_value"] = old_value
    data[key].append(entry)
    _save(vault_path, data)


def get_history(vault_path: str, key: str) -> list:
    """Return list of history entries for a key."""
    data = _load(vault_path)
    return data.get(key, [])


def clear_history(vault_path: str, key: Optional[str] = None) -> None:
    """Clear history for a specific key or all keys."""
    if key is None:
        hp = _history_path(vault_path)
        if hp.exists():
            hp.unlink()
    else:
        data = _load(vault_path)
        data.pop(key, None)
        _save(vault_path, data)
