"""Diff two vault states or compare local vault against a remote snapshot."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from envault.vault import load_vault


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


def diff_vaults(
    old: Dict[str, str],
    new: Dict[str, str],
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare two plain-text dicts of env vars and return diff entries."""
    entries: List[DiffEntry] = []
    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key in old and key not in new:
            entries.append(DiffEntry(key=key, status="removed", old_value=old[key]))
        elif key not in old and key in new:
            entries.append(DiffEntry(key=key, status="added", new_value=new[key]))
        elif old[key] != new[key]:
            entries.append(DiffEntry(key=key, status="changed", old_value=old[key], new_value=new[key]))
        elif show_unchanged:
            entries.append(DiffEntry(key=key, status="unchanged", old_value=old[key], new_value=new[key]))
    return entries


def diff_vault_files(
    old_path: str,
    new_path: str,
    password: str,
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Load two encrypted vault files and diff them."""
    old_data = load_vault(old_path, password)
    new_data = load_vault(new_path, password)
    return diff_vaults(old_data, new_data, show_unchanged=show_unchanged)
