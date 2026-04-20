"""Alias support: give a short name to a vault key."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from envault.vault import load_vault, save_vault, get_var, set_var

_ALIAS_NS = "__aliases__"


def _get_aliases(vault_path: Path, password: str) -> Dict[str, str]:
    """Return the alias map {alias: real_key}."""
    vault = load_vault(vault_path, password)
    return dict(vault.get(_ALIAS_NS, {}))


def _save_aliases(vault_path: Path, password: str, aliases: Dict[str, str]) -> None:
    vault = load_vault(vault_path, password)
    vault[_ALIAS_NS] = aliases
    save_vault(vault_path, password, vault)


def add_alias(vault_path: Path, password: str, alias: str, key: str) -> None:
    """Create *alias* pointing to *key*. Raises KeyError if *key* does not exist."""
    vault = load_vault(vault_path, password)
    if key not in vault or key == _ALIAS_NS:
        raise KeyError(f"Key '{key}' not found in vault")
    aliases = dict(vault.get(_ALIAS_NS, {}))
    aliases[alias] = key
    vault[_ALIAS_NS] = aliases
    save_vault(vault_path, password, vault)


def remove_alias(vault_path: Path, password: str, alias: str) -> None:
    """Delete *alias*. Raises KeyError if alias does not exist."""
    aliases = _get_aliases(vault_path, password)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found")
    del aliases[alias]
    _save_aliases(vault_path, password, aliases)


def resolve_alias(vault_path: Path, password: str, alias: str) -> Optional[str]:
    """Return the real key for *alias*, or None if not defined."""
    aliases = _get_aliases(vault_path, password)
    return aliases.get(alias)


def get_via_alias(vault_path: Path, password: str, alias: str) -> str:
    """Resolve *alias* and return the variable value. Raises KeyError if missing."""
    real_key = resolve_alias(vault_path, password, alias)
    if real_key is None:
        raise KeyError(f"Alias '{alias}' not found")
    return get_var(vault_path, password, real_key)


def list_aliases(vault_path: Path, password: str) -> Dict[str, str]:
    """Return all aliases as {alias: real_key}."""
    return _get_aliases(vault_path, password)
