"""Annotations: attach arbitrary metadata notes to vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.vault import load_vault


class AnnotationError(Exception):
    pass


def _annotations_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".annotations.json")


def _load(vault_path: str) -> dict:
    p = _annotations_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _annotations_path(vault_path).write_text(json.dumps(data, indent=2))


def set_annotation(vault_path: str, password: str, key: str, note: str) -> None:
    """Attach a text note to *key*. Raises AnnotationError if key not in vault."""
    vault = load_vault(vault_path, password)
    if key not in vault:
        raise AnnotationError(f"Key '{key}' not found in vault.")
    data = _load(vault_path)
    data[key] = note
    _save(vault_path, data)


def get_annotation(vault_path: str, key: str) -> str | None:
    """Return the note for *key*, or None if no annotation exists."""
    return _load(vault_path).get(key)


def remove_annotation(vault_path: str, key: str) -> None:
    """Delete the annotation for *key*. Raises AnnotationError if none."""
    data = _load(vault_path)
    if key not in data:
        raise AnnotationError(f"No annotation found for key '{key}'.")
    del data[key]
    _save(vault_path, data)


def list_annotations(vault_path: str) -> dict[str, str]:
    """Return all key -> note mappings."""
    return dict(_load(vault_path))
