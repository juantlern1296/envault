"""Clone (copy) variables between vaults or profiles."""
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault


class CloneError(Exception):
    pass


def clone_var(
    src_path: str,
    src_password: str,
    dst_path: str,
    dst_password: str,
    key: str,
    dest_key: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    """Copy a single variable from one vault to another.

    Returns the destination key name.
    """
    src = Path(src_path)
    dst = Path(dst_path)

    src_data = load_vault(src, src_password)
    if key not in src_data:
        raise CloneError(f"Key '{key}' not found in source vault")

    dest_key = dest_key or key
    dst_data = load_vault(dst, dst_password) if dst.exists() else {}

    if dest_key in dst_data and not overwrite:
        raise CloneError(
            f"Key '{dest_key}' already exists in destination vault. "
            "Use overwrite=True to replace it."
        )

    dst_data[dest_key] = src_data[key]
    save_vault(dst, dst_password, dst_data)
    return dest_key


def clone_all(
    src_path: str,
    src_password: str,
    dst_path: str,
    dst_password: str,
    overwrite: bool = False,
) -> dict:
    """Copy all variables from one vault to another.

    Returns a dict mapping key -> 'ok' | 'skipped'.
    """
    src = Path(src_path)
    dst = Path(dst_path)

    src_data = load_vault(src, src_password)
    dst_data = load_vault(dst, dst_password) if dst.exists() else {}

    results = {}
    for key, value in src_data.items():
        if key in dst_data and not overwrite:
            results[key] = "skipped"
        else:
            dst_data[key] = value
            results[key] = "ok"

    save_vault(dst, dst_password, dst_data)
    return results
