"""Cascade: propagate a variable's value to a set of dependent keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envault.vault import get_var, set_var, load_vault


class CascadeError(Exception):
    pass


@dataclass
class CascadeResult:
    source_key: str
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)


def cascade_var(
    vault_path: str,
    password: str,
    source_key: str,
    target_keys: List[str],
    overwrite: bool = True,
) -> CascadeResult:
    """Copy the value of *source_key* to every key in *target_keys*."""
    try:
        source_value = get_var(vault_path, password, source_key)
    except KeyError:
        raise CascadeError(f"Source key '{source_key}' does not exist in vault.")

    result = CascadeResult(source_key=source_key)
    vault = load_vault(vault_path, password)

    for key in target_keys:
        if not overwrite and key in vault:
            result.skipped.append(key)
            continue
        try:
            set_var(vault_path, password, key, source_value)
            result.updated.append(key)
        except Exception:
            result.failed.append(key)

    return result


def cascade_all(
    vault_path: str,
    password: str,
    mapping: dict,
    overwrite: bool = True,
) -> List[CascadeResult]:
    """Run cascade_var for each source -> [targets] pair in *mapping*."""
    results = []
    for source_key, target_keys in mapping.items():
        results.append(
            cascade_var(vault_path, password, source_key, target_keys, overwrite)
        )
    return results
