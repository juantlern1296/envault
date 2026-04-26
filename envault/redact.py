"""Redaction helpers — mask sensitive values before display or logging."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from envault.vault import load_vault

# Keys whose values should always be fully hidden
_ALWAYS_REDACT_PATTERNS: List[re.Pattern] = [
    re.compile(r"(password|passwd|secret|token|api[_-]?key|private[_-]?key)", re.I),
]

DEFAULT_MASK = "****"
PARTIAL_VISIBLE = 4  # characters to reveal at the end for partial mode


def _key_is_sensitive(key: str) -> bool:
    """Return True if the key name matches a known-sensitive pattern."""
    return any(p.search(key) for p in _ALWAYS_REDACT_PATTERNS)


def redact_value(
    key: str,
    value: str,
    *,
    partial: bool = False,
    mask: str = DEFAULT_MASK,
) -> str:
    """Return a redacted representation of *value*.

    If *partial* is True and the value is long enough, reveal the last
    ``PARTIAL_VISIBLE`` characters so users can verify the correct secret
    is present without exposing it fully.
    """
    if not _key_is_sensitive(key):
        return value

    if partial and len(value) > PARTIAL_VISIBLE:
        return mask + value[-PARTIAL_VISIBLE:]

    return mask


def redact_dict(
    data: Dict[str, str],
    *,
    partial: bool = False,
    mask: str = DEFAULT_MASK,
) -> Dict[str, str]:
    """Return a copy of *data* with sensitive values redacted."""
    return {
        k: redact_value(k, v, partial=partial, mask=mask)
        for k, v in data.items()
    }


def redact_vault(
    vault_path: str,
    password: str,
    *,
    partial: bool = False,
    mask: str = DEFAULT_MASK,
) -> Dict[str, str]:
    """Load the vault and return a redacted view of all variables."""
    data = load_vault(vault_path, password)
    return redact_dict(data, partial=partial, mask=mask)
