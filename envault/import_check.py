"""Check for duplicate or conflicting keys when importing variables."""

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault


@dataclass
class ConflictEntry:
    key: str
    existing_value: str
    incoming_value: str
    is_duplicate: bool  # True if values are identical, False if conflicting


def check_import_conflicts(
    vault_path: str,
    password: str,
    incoming: dict[str, str],
) -> list[ConflictEntry]:
    """Compare incoming key/value pairs against the current vault.

    Returns a list of ConflictEntry for any key that already exists,
    whether the value is identical (duplicate) or different (conflict).
    """
    try:
        existing = load_vault(vault_path, password)
    except FileNotFoundError:
        existing = {}

    conflicts: list[ConflictEntry] = []
    for key, incoming_val in incoming.items():
        if key in existing:
            existing_val = existing[key]
            conflicts.append(
                ConflictEntry(
                    key=key,
                    existing_value=existing_val,
                    incoming_value=incoming_val,
                    is_duplicate=(existing_val == incoming_val),
                )
            )
    return conflicts


def summarise_conflicts(conflicts: list[ConflictEntry]) -> str:
    """Return a human-readable summary of import conflicts."""
    if not conflicts:
        return "No conflicts found."

    lines = []
    for c in conflicts:
        if c.is_duplicate:
            lines.append(f"  [duplicate]  {c.key} (same value already stored)")
        else:
            lines.append(
                f"  [conflict]   {c.key} "
                f"(existing: {c.existing_value!r}, incoming: {c.incoming_value!r})"
            )
    return "\n".join(lines)
