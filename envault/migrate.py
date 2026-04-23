"""Vault migration: apply versioned transformations to vault data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envault.vault import load_vault, save_vault


@dataclass
class MigrationResult:
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors


# Registry: version_tag -> transform(data: dict) -> dict
_MIGRATIONS: Dict[str, Callable[[dict], dict]] = {}

_META_KEY = "__envault_migrations__"


def register_migration(version: str) -> Callable:
    """Decorator to register a migration function."""
    def decorator(fn: Callable[[dict], dict]) -> Callable:
        _MIGRATIONS[version] = fn
        return fn
    return decorator


def _applied_versions(data: dict) -> List[str]:
    return data.get(_META_KEY, [])


def _mark_applied(data: dict, version: str) -> dict:
    applied = list(data.get(_META_KEY, []))
    if version not in applied:
        applied.append(version)
    data[_META_KEY] = applied
    return data


def run_migrations(
    vault_path: str,
    password: str,
    versions: Optional[List[str]] = None,
) -> MigrationResult:
    """Apply pending migrations to the vault in order."""
    data = load_vault(vault_path, password)
    applied_set = set(_applied_versions(data))
    targets = versions if versions is not None else sorted(_MIGRATIONS.keys())
    result = MigrationResult()

    for version in targets:
        if version in applied_set:
            result.skipped.append(version)
            continue
        if version not in _MIGRATIONS:
            result.errors[version] = "migration not found"
            continue
        try:
            data = _MIGRATIONS[version](data)
            data = _mark_applied(data, version)
            result.applied.append(version)
        except Exception as exc:  # noqa: BLE001
            result.errors[version] = str(exc)
            break

    save_vault(vault_path, password, data)
    return result


def list_migrations(vault_path: str, password: str) -> Dict[str, str]:
    """Return status of all registered migrations for this vault."""
    data = load_vault(vault_path, password)
    applied_set = set(_applied_versions(data))
    return {
        v: ("applied" if v in applied_set else "pending")
        for v in sorted(_MIGRATIONS.keys())
    }
