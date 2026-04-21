"""Checkpoint support: mark named points in vault history for quick reference."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.vault import load_vault


class CheckpointError(Exception):
    pass


def _checkpoints_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".checkpoints.json")


def _load(vault_file: str) -> dict[str, Any]:
    p = _checkpoints_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_file: str, data: dict[str, Any]) -> None:
    _checkpoints_path(vault_file).write_text(json.dumps(data, indent=2))


def create_checkpoint(vault_file: str, password: str, name: str) -> None:
    """Snapshot the current vault state under *name*."""
    if not name or not name.strip():
        raise CheckpointError("Checkpoint name must not be empty.")
    data = _load(vault_file)
    state = load_vault(vault_file, password)
    data[name] = state
    _save(vault_file, data)


def list_checkpoints(vault_file: str) -> list[str]:
    """Return all checkpoint names in insertion order."""
    return list(_load(vault_file).keys())


def restore_checkpoint(vault_file: str, password: str, name: str) -> dict[str, str]:
    """Return the vault state stored at *name* (does not overwrite live vault)."""
    data = _load(vault_file)
    if name not in data:
        raise CheckpointError(f"Checkpoint '{name}' not found.")
    return dict(data[name])


def delete_checkpoint(vault_file: str, name: str) -> None:
    """Remove a named checkpoint."""
    data = _load(vault_file)
    if name not in data:
        raise CheckpointError(f"Checkpoint '{name}' not found.")
    del data[name]
    _save(vault_file, data)
