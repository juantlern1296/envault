"""Promote variables from one profile/namespace to another (e.g. staging -> production)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault


@dataclass
class PromoteResult:
    promoted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.promoted) > 0 or len(self.overwritten) > 0


class PromoteError(Exception):
    pass


def promote_var(
    vault_path: str,
    password: str,
    key: str,
    src_namespace: str,
    dst_namespace: str,
    overwrite: bool = False,
) -> PromoteResult:
    """Copy a single variable from src_namespace to dst_namespace."""
    result = PromoteResult()
    data = load_vault(vault_path, password)

    src_key = f"{src_namespace}:{key}"
    dst_key = f"{dst_namespace}:{key}"

    if src_key not in data:
        raise PromoteError(f"Key '{key}' not found in namespace '{src_namespace}'")

    value = data[src_key]

    if dst_key in data and not overwrite:
        result.skipped.append(key)
        return result

    if dst_key in data and overwrite:
        result.overwritten.append(key)
    else:
        result.promoted.append(key)

    data[dst_key] = value
    save_vault(vault_path, password, data)
    return result


def promote_all(
    vault_path: str,
    password: str,
    src_namespace: str,
    dst_namespace: str,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> PromoteResult:
    """Promote all (or a subset of) variables from src_namespace to dst_namespace."""
    result = PromoteResult()
    data = load_vault(vault_path, password)

    prefix = f"{src_namespace}:"
    src_items: Dict[str, str] = {
        k[len(prefix):]: v for k, v in data.items() if k.startswith(prefix)
    }

    if keys is not None:
        src_items = {k: v for k, v in src_items.items() if k in keys}

    for key, value in src_items.items():
        dst_key = f"{dst_namespace}:{key}"
        if dst_key in data and not overwrite:
            result.skipped.append(key)
            continue
        if dst_key in data:
            result.overwritten.append(key)
        else:
            result.promoted.append(key)
        data[dst_key] = value

    save_vault(vault_path, password, data)
    return result
