"""Batch operations: set/delete multiple vars at once."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import get_var, set_var, delete_var, load_vault


@dataclass
class BatchResult:
    succeeded: List[str] = field(default_factory=list)
    failed: Dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0


def batch_set(
    vault_path: str,
    password: str,
    pairs: Dict[str, str],
    *,
    stop_on_error: bool = False,
) -> BatchResult:
    """Set multiple key/value pairs in one call."""
    result = BatchResult()
    for key, value in pairs.items():
        try:
            set_var(vault_path, password, key, value)
            result.succeeded.append(key)
        except Exception as exc:  # noqa: BLE001
            result.failed[key] = str(exc)
            if stop_on_error:
                break
    return result


def batch_delete(
    vault_path: str,
    password: str,
    keys: List[str],
    *,
    stop_on_error: bool = False,
) -> BatchResult:
    """Delete multiple keys in one call."""
    result = BatchResult()
    for key in keys:
        try:
            delete_var(vault_path, password, key)
            result.succeeded.append(key)
        except Exception as exc:  # noqa: BLE001
            result.failed[key] = str(exc)
            if stop_on_error:
                break
    return result


def batch_get(
    vault_path: str,
    password: str,
    keys: List[str],
) -> Dict[str, Optional[str]]:
    """Retrieve multiple keys; missing keys map to None."""
    data = load_vault(vault_path, password)
    return {key: data.get(key) for key in keys}
