"""Access control: restrict which keys a given 'role' can read or write."""

from __future__ import annotations

from typing import Dict, List

from envault.vault import load_vault, save_vault

_ACCESS_NS = "__access__"


def _get_acl(vault_path: str, password: str) -> Dict[str, Dict[str, List[str]]]:
    """Return the raw ACL dict stored in the vault."""
    data = load_vault(vault_path, password)
    raw = data.get(_ACCESS_NS, {})
    if not isinstance(raw, dict):
        return {}
    return raw


def _save_acl(vault_path: str, password: str, acl: Dict[str, Dict[str, List[str]]]) -> None:
    data = load_vault(vault_path, password)
    data[_ACCESS_NS] = acl
    save_vault(vault_path, password, data)


def grant(vault_path: str, password: str, role: str, key: str, permission: str) -> None:
    """Grant *role* the given *permission* ('read' or 'write') on *key*."""
    if permission not in ("read", "write"):
        raise ValueError(f"Unknown permission '{permission}'; expected 'read' or 'write'")
    acl = _get_acl(vault_path, password)
    role_entry = acl.setdefault(role, {"read": [], "write": []})
    if key not in role_entry[permission]:
        role_entry[permission].append(key)
    _save_acl(vault_path, password, acl)


def revoke(vault_path: str, password: str, role: str, key: str, permission: str) -> None:
    """Revoke *permission* on *key* from *role*."""
    if permission not in ("read", "write"):
        raise ValueError(f"Unknown permission '{permission}'; expected 'read' or 'write'")
    acl = _get_acl(vault_path, password)
    role_entry = acl.get(role, {})
    keys = role_entry.get(permission, [])
    if key not in keys:
        raise KeyError(f"Role '{role}' has no '{permission}' permission on '{key}'")
    keys.remove(key)
    _save_acl(vault_path, password, acl)


def can(vault_path: str, password: str, role: str, key: str, permission: str) -> bool:
    """Return True if *role* holds *permission* on *key*."""
    acl = _get_acl(vault_path, password)
    return key in acl.get(role, {}).get(permission, [])


def list_permissions(vault_path: str, password: str, role: str) -> Dict[str, List[str]]:
    """Return the full permission map for *role*."""
    acl = _get_acl(vault_path, password)
    return acl.get(role, {"read": [], "write": []})


def list_roles(vault_path: str, password: str) -> List[str]:
    """Return all roles that have at least one permission entry."""
    return list(_get_acl(vault_path, password).keys())
