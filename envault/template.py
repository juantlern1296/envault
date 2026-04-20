"""Template rendering: substitute vault variables into template strings."""

import re
from typing import Optional

from envault.vault import load_vault

_PATTERN = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


def render_string(template: str, vault_path: str, password: str) -> str:
    """Replace {{VAR_NAME}} placeholders with values from the vault."""
    data = load_vault(vault_path, password)

    missing: list[str] = []

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key not in data:
            missing.append(key)
            return match.group(0)  # leave placeholder intact
        return data[key]

    result = _PATTERN.sub(replacer, template)

    if missing:
        raise KeyError(f"Template references missing vault keys: {', '.join(missing)}")

    return result


def render_file(
    src_path: str,
    dst_path: str,
    vault_path: str,
    password: str,
    strict: bool = True,
) -> list[str]:
    """Render *src_path* template into *dst_path*.

    Returns list of substituted variable names.
    If *strict* is False, unknown placeholders are left as-is instead of
    raising an error.
    """
    with open(src_path, "r") as fh:
        template = fh.read()

    if strict:
        rendered = render_string(template, vault_path, password)
    else:
        data = load_vault(vault_path, password)
        rendered = _PATTERN.sub(
            lambda m: data.get(m.group(1), m.group(0)), template
        )

    with open(dst_path, "w") as fh:
        fh.write(rendered)

    found = _PATTERN.findall(template)
    return list(dict.fromkeys(found))  # deduplicated, order-preserving
