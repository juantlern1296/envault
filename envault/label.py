"""Label support — attach arbitrary key/value metadata labels to vault variables."""
from __future__ import annotations

from typing import Any

from envault.vault import load_vault, save_vault

_LABELS_KEY = "__labels__"


class LabelError(Exception):
    pass


def _get_labels(vault_path: str, password: str) -> dict[str, dict[str, str]]:
    data = load_vault(vault_path, password)
    return data.get(_LABELS_KEY, {})


def _save_labels(
    vault_path: str, password: str, labels: dict[str, dict[str, str]]
) -> None:
    data = load_vault(vault_path, password)
    data[_LABELS_KEY] = labels
    save_vault(vault_path, password, data)


def set_label(vault_path: str, password: str, key: str, label: str, value: str) -> None:
    """Attach *label=value* to *key*.  Raises LabelError if the key does not exist."""
    data = load_vault(vault_path, password)
    if key not in data:
        raise LabelError(f"key '{key}' not found in vault")
    labels = data.get(_LABELS_KEY, {})
    labels.setdefault(key, {})[label] = value
    data[_LABELS_KEY] = labels
    save_vault(vault_path, password, data)


def remove_label(vault_path: str, password: str, key: str, label: str) -> None:
    """Remove a single label from *key*.  Raises LabelError if not present."""
    labels = _get_labels(vault_path, password)
    if key not in labels or label not in labels[key]:
        raise LabelError(f"label '{label}' not found on key '{key}'")
    del labels[key][label]
    if not labels[key]:
        del labels[key]
    _save_labels(vault_path, password, labels)


def get_labels(vault_path: str, password: str, key: str) -> dict[str, str]:
    """Return all labels attached to *key* (empty dict if none)."""
    labels = _get_labels(vault_path, password)
    return dict(labels.get(key, {}))


def find_by_label(
    vault_path: str, password: str, label: str, value: str | None = None
) -> list[str]:
    """Return keys that have *label* set, optionally filtered by *value*."""
    labels = _get_labels(vault_path, password)
    result = []
    for k, lmap in labels.items():
        if label in lmap:
            if value is None or lmap[label] == value:
                result.append(k)
    return sorted(result)
