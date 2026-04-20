"""Pin specific vault variable versions so they are protected from overwrites."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.vault import load_vault, save_vault

_PINS_KEY = "__pins__"


def _get_pins(vault_path: Path, password: str) -> dict[str, Any]:
    data = load_vault(vault_path, password)
    return data.get(_PINS_KEY, {})


def _save_pins(vault_path: Path, password: str, pins: dict[str, Any]) -> None:
    data = load_vault(vault_path, password)
    data[_PINS_KEY] = pins
    save_vault(vault_path, password, data)


def pin_var(vault_path: Path, password: str, key: str) -> None:
    """Pin a variable so it cannot be overwritten until unpinned."""
    data = load_vault(vault_path, password)
    if key not in data or key == _PINS_KEY:
        raise KeyError(f"Variable '{key}' not found in vault")
    pins = _get_pins(vault_path, password)
    pins[key] = data[key]
    _save_pins(vault_path, password, pins)


def unpin_var(vault_path: Path, password: str, key: str) -> None:
    """Remove the pin from a variable."""
    pins = _get_pins(vault_path, password)
    if key not in pins:
        raise KeyError(f"Variable '{key}' is not pinned")
    del pins[key]
    _save_pins(vault_path, password, pins)


def is_pinned(vault_path: Path, password: str, key: str) -> bool:
    """Return True if the variable is currently pinned."""
    pins = _get_pins(vault_path, password)
    return key in pins


def list_pinned(vault_path: Path, password: str) -> list[str]:
    """Return a sorted list of all pinned variable names."""
    pins = _get_pins(vault_path, password)
    return sorted(pins.keys())


def assert_not_pinned(vault_path: Path, password: str, key: str) -> None:
    """Raise ValueError if the variable is pinned (used before writes)."""
    if is_pinned(vault_path, password, key):
        raise ValueError(
            f"Variable '{key}' is pinned and cannot be overwritten. "
            "Unpin it first with 'envault pin unpin <key>'."
        )
