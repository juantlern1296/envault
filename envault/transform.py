"""Value transformation pipelines for vault entries."""
from __future__ import annotations

import base64
import re
from typing import Callable

from envault.vault import load_vault, save_vault

# Registry of named transforms
_TRANSFORMS: dict[str, Callable[[str], str]] = {}


class TransformError(Exception):
    pass


def register(name: str) -> Callable:
    def decorator(fn: Callable[[str], str]) -> Callable:
        _TRANSFORMS[name] = fn
        return fn
    return decorator


@register("upper")
def _upper(value: str) -> str:
    return value.upper()


@register("lower")
def _lower(value: str) -> str:
    return value.lower()


@register("strip")
def _strip(value: str) -> str:
    return value.strip()


@register("base64encode")
def _b64encode(value: str) -> str:
    return base64.b64encode(value.encode()).decode()


@register("base64decode")
def _b64decode(value: str) -> str:
    try:
        return base64.b64decode(value.encode()).decode()
    except Exception as exc:
        raise TransformError(f"base64decode failed: {exc}") from exc


@register("urlencode")
def _urlencode(value: str) -> str:
    from urllib.parse import quote
    return quote(value, safe="")


def list_transforms() -> list[str]:
    """Return the names of all registered transforms."""
    return sorted(_TRANSFORMS.keys())


def apply_transform(name: str, value: str) -> str:
    """Apply a single named transform to *value*."""
    if name not in _TRANSFORMS:
        raise TransformError(f"Unknown transform: {name!r}. Available: {list_transforms()}")
    return _TRANSFORMS[name](value)


def apply_pipeline(value: str, pipeline: list[str]) -> str:
    """Apply a list of transforms in order."""
    for name in pipeline:
        value = apply_transform(name, value)
    return value


def transform_var(
    vault_path: str,
    password: str,
    key: str,
    pipeline: list[str],
    *,
    dry_run: bool = False,
) -> str:
    """Load *key* from vault, run *pipeline*, optionally save result. Returns new value."""
    data = load_vault(vault_path, password)
    if key not in data:
        raise TransformError(f"Key {key!r} not found in vault")
    original = data[key]
    transformed = apply_pipeline(original, pipeline)
    if not dry_run:
        data[key] = transformed
        save_vault(vault_path, password, data)
    return transformed
