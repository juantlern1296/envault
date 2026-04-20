"""Search/filter vault variables by key pattern or value."""
from __future__ import annotations
import fnmatch
from typing import Optional
from envault.vault import load_vault


def search_vars(
    vault_path: str,
    password: str,
    pattern: str,
    search_values: bool = False,
    profile: Optional[str] = None,
) -> dict[str, str]:
    """Return vars whose key (or optionally value) matches *pattern* (glob).

    Args:
        vault_path: Path to the vault file.
        password: Vault password.
        pattern: Glob pattern to match against keys (and values if search_values).
        search_values: If True also match against values.
        profile: Optional profile namespace to search within.

    Returns:
        Dict of matching key→value pairs.
    """
    data = load_vault(vault_path, password)

    if profile is not None:
        prefix = f"profile:{profile}:"
        subset = {
            k[len(prefix):]: v
            for k, v in data.items()
            if k.startswith(prefix)
        }
    else:
        subset = {
            k: v for k, v in data.items()
            if not k.startswith("profile:")
            and not k.startswith("__")
        }

    results: dict[str, str] = {}
    for key, value in subset.items():
        key_match = fnmatch.fnmatch(key, pattern)
        val_match = search_values and fnmatch.fnmatch(str(value), pattern)
        if key_match or val_match:
            results[key] = value

    return results
