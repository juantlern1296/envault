"""mask.py — control which vault keys are masked in output by default."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault.vault import load_vault


class MaskError(Exception):
    pass


def _mask_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".masks.json")


def _load(vault_file: str) -> dict:
    p = _mask_path(vault_file)
    if not p.exists():
        return {"masked": []}
    return json.loads(p.read_text())


def _save(vault_file: str, data: dict) -> None:
    _mask_path(vault_file).write_text(json.dumps(data, indent=2))


def mask_var(vault_file: str, password: str, key: str) -> None:
    """Mark *key* as masked. Raises MaskError if the key does not exist."""
    vault = load_vault(vault_file, password)
    if key not in vault:
        raise MaskError(f"Key '{key}' not found in vault")
    data = _load(vault_file)
    if key not in data["masked"]:
        data["masked"].append(key)
        _save(vault_file, data)


def unmask_var(vault_file: str, key: str) -> None:
    """Remove *key* from the masked list. No-op if not masked."""
    data = _load(vault_file)
    if key in data["masked"]:
        data["masked"].remove(key)
        _save(vault_file, data)


def is_masked(vault_file: str, key: str) -> bool:
    """Return True if *key* is in the masked list."""
    return key in _load(vault_file)["masked"]


def list_masked(vault_file: str) -> List[str]:
    """Return all keys currently marked as masked."""
    return list(_load(vault_file)["masked"])


def apply_mask(vault_file: str, data: dict, placeholder: str = "***") -> dict:
    """Return a copy of *data* with masked values replaced by *placeholder*."""
    masked_keys = set(_load(vault_file)["masked"])
    return {k: (placeholder if k in masked_keys else v) for k, v in data.items()}
