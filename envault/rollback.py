"""Rollback support: restore a vault to a previous state from history."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.history import get_history, _history_path, _load as _load_history, _save as _save_history
from envault.vault import load_vault, save_vault


class RollbackError(Exception):
    pass


def list_rollback_points(vault_path: str, password: str) -> list[dict]:
    """Return a list of rollback points (history entries) for a vault."""
    history_file = _history_path(vault_path)
    if not Path(history_file).exists():
        return []
    entries = _load_history(history_file)
    return list(reversed(entries))


def rollback_to(vault_path: str, password: str, index: int) -> dict:
    """Restore the vault to the state captured at the given history index.

    index 0 = most recent change, 1 = one before that, etc.
    Returns the restored key/value mapping.
    """
    points = list_rollback_points(vault_path, password)
    if not points:
        raise RollbackError("No rollback points available.")
    if index < 0 or index >= len(points):
        raise RollbackError(
            f"Index {index} out of range (0..{len(points) - 1})."
        )

    target = points[index]
    key: str = target["key"]
    action: str = target["action"]
    old_value: Optional[str] = target.get("old_value")

    data = load_vault(vault_path, password)

    if action == "set":
        # Undo a set: restore old value or delete if there was none
        if old_value is None:
            data.pop(key, None)
        else:
            data[key] = old_value
    elif action == "delete":
        # Undo a delete: put the old value back
        if old_value is not None:
            data[key] = old_value
    else:
        raise RollbackError(f"Unknown action '{action}' in history entry.")

    save_vault(vault_path, password, data)
    return data
