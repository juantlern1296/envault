"""Vault compression — gzip-compress/decompress vault payloads before encryption."""

import gzip
import json
from pathlib import Path
from typing import Any

from envault.vault import load_vault, save_vault


_COMPRESS_MARKER = "__compressed__"


def compress_vault(vault_path: Path, password: str) -> int:
    """Compress all string values in the vault in-place.

    Returns the number of values compressed.
    """
    data = load_vault(vault_path, password)
    count = 0
    for key, value in data.items():
        if isinstance(value, str) and not _is_compressed(value):
            data[key] = _compress_value(value)
            count += 1
    save_vault(vault_path, password, data)
    return count


def decompress_vault(vault_path: Path, password: str) -> int:
    """Decompress all compressed values in the vault in-place.

    Returns the number of values decompressed.
    """
    data = load_vault(vault_path, password)
    count = 0
    for key, value in data.items():
        if isinstance(value, str) and _is_compressed(value):
            data[key] = _decompress_value(value)
            count += 1
    save_vault(vault_path, password, data)
    return count


def compress_ratio(vault_path: Path, password: str) -> dict[str, float]:
    """Return per-key compression ratio (compressed_size / original_size).

    Only keys that are currently compressed are included.
    """
    data = load_vault(vault_path, password)
    ratios: dict[str, float] = {}
    for key, value in data.items():
        if isinstance(value, str) and _is_compressed(value):
            raw = _decompress_value(value)
            original_size = len(raw.encode())
            compressed_size = len(value.encode())
            ratios[key] = round(compressed_size / original_size, 4) if original_size else 1.0
    return ratios


def _compress_value(value: str) -> str:
    """Compress a string and encode as a marker-prefixed hex string."""
    compressed = gzip.compress(value.encode("utf-8"))
    return f"{_COMPRESS_MARKER}:{compressed.hex()}"


def _decompress_value(value: str) -> str:
    """Decompress a marker-prefixed hex string back to a plain string."""
    hex_data = value[len(_COMPRESS_MARKER) + 1:]
    return gzip.decompress(bytes.fromhex(hex_data)).decode("utf-8")


def _is_compressed(value: str) -> bool:
    return value.startswith(f"{_COMPRESS_MARKER}:")
