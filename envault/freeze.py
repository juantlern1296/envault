"""Freeze/unfreeze vault keys to prevent accidental modification."""

from __future__ import annotations

from pathlib import Path
from typing import List

from envault.vault import load_vault, save_vault


class FreezeError(Exception):
    pass


def _freeze_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".frozen.json")


def _load_frozen(vault_path: str) -> dict:
    import json
    p = _freeze_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_frozen(vault_path: str, data: dict) -> None:
    import json
    p = _freeze_path(vault_path)
    p.write_text(json.dumps(data, indent=2))


def freeze_var(vault_path: str, password: str, key: str) -> None:
    """Mark a key as frozen; raises FreezeError if key does not exist."""
    vault = load_vault(vault_path, password)
    if key not in vault:
        raise FreezeError(f"Key '{key}' not found in vault.")
    frozen = _load_frozen(vault_path)
    frozen[key] = True
    _save_frozen(vault_path, frozen)


def unfreeze_var(vault_path: str, key: str) -> None:
    """Remove freeze on a key; raises FreezeError if key is not frozen."""
    frozen = _load_frozen(vault_path)
    if key not in frozen:
        raise FreezeError(f"Key '{key}' is not frozen.")
    del frozen[key]
    _save_frozen(vault_path, frozen)


def is_frozen(vault_path: str, key: str) -> bool:
    """Return True if the key is currently frozen."""
    return _load_frozen(vault_path).get(key, False)


def list_frozen(vault_path: str) -> List[str]:
    """Return a sorted list of all frozen keys."""
    return sorted(_load_frozen(vault_path).keys())


def assert_not_frozen(vault_path: str, key: str) -> None:
    """Raise FreezeError if the key is frozen."""
    if is_frozen(vault_path, key):
        raise FreezeError(f"Key '{key}' is frozen and cannot be modified.")
