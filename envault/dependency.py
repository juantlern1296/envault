"""Variable dependency tracking — define which vars depend on others."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envault.vault import load_vault


def _deps_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".deps.json")


def _load(vault_path: str) -> Dict[str, List[str]]:
    p = _deps_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, deps: Dict[str, List[str]]) -> None:
    _deps_path(vault_path).write_text(json.dumps(deps, indent=2))


def add_dependency(vault_path: str, password: str, key: str, depends_on: str) -> None:
    """Record that *key* depends on *depends_on*."""
    vault = load_vault(vault_path, password)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault")
    if depends_on not in vault:
        raise KeyError(f"Key '{depends_on}' not found in vault")
    if key == depends_on:
        raise ValueError("A key cannot depend on itself")
    deps = _load(vault_path)
    existing = deps.get(key, [])
    if depends_on not in existing:
        existing.append(depends_on)
    deps[key] = existing
    _save(vault_path, deps)


def remove_dependency(vault_path: str, key: str, depends_on: str) -> None:
    deps = _load(vault_path)
    if key not in deps or depends_on not in deps[key]:
        raise KeyError(f"Dependency '{key}' -> '{depends_on}' not found")
    deps[key].remove(depends_on)
    if not deps[key]:
        del deps[key]
    _save(vault_path, deps)


def list_dependencies(vault_path: str, key: str) -> List[str]:
    """Return the list of keys that *key* directly depends on."""
    return _load(vault_path).get(key, [])


def dependents_of(vault_path: str, key: str) -> List[str]:
    """Return keys that directly depend on *key*."""
    deps = _load(vault_path)
    return [k for k, v in deps.items() if key in v]


def resolve_order(vault_path: str) -> List[str]:
    """Topological sort of all keys with dependencies (leaves first)."""
    deps = _load(vault_path)
    visited: set = set()
    order: List[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return
        visited.add(node)
        for dep in deps.get(node, []):
            visit(dep)
        order.append(node)

    for key in deps:
        visit(key)
    return order
