"""Schema validation for vault variables."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from envault.vault import load_vault, save_vault

SCHEMA_KEY = "__schemas__"

VALID_TYPES = {"string", "integer", "float", "boolean", "url", "email"}

_URL_RE = re.compile(r"^https?://[^\s]+$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class SchemaEntry:
    type: str = "string"
    required: bool = False
    pattern: Optional[str] = None
    description: str = ""


class SchemaViolation(Exception):
    pass


def _get_schemas(vault_path: str, password: str) -> dict:
    data = load_vault(vault_path, password)
    return data.get(SCHEMA_KEY, {})


def _save_schemas(vault_path: str, password: str, schemas: dict) -> None:
    data = load_vault(vault_path, password)
    data[SCHEMA_KEY] = schemas
    save_vault(vault_path, password, data)


def set_schema(
    vault_path: str,
    password: str,
    key: str,
    type: str = "string",
    required: bool = False,
    pattern: Optional[str] = None,
    description: str = "",
) -> None:
    if type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{type}'. Must be one of: {', '.join(sorted(VALID_TYPES))}")
    schemas = _get_schemas(vault_path, password)
    schemas[key] = {"type": type, "required": required, "pattern": pattern, "description": description}
    _save_schemas(vault_path, password, schemas)


def get_schema(vault_path: str, password: str, key: str) -> Optional[SchemaEntry]:
    schemas = _get_schemas(vault_path, password)
    if key not in schemas:
        return None
    s = schemas[key]
    return SchemaEntry(**s)


def delete_schema(vault_path: str, password: str, key: str) -> None:
    schemas = _get_schemas(vault_path, password)
    if key not in schemas:
        raise KeyError(f"No schema defined for '{key}'")
    del schemas[key]
    _save_schemas(vault_path, password, schemas)


def validate_var(vault_path: str, password: str, key: str, value: str) -> None:
    """Validate a value against the schema for the given key. Raises SchemaViolation on failure."""
    schema = get_schema(vault_path, password, key)
    if schema is None:
        return

    t = schema.type
    if t == "integer":
        try:
            int(value)
        except ValueError:
            raise SchemaViolation(f"'{key}' must be an integer, got: {value!r}")
    elif t == "float":
        try:
            float(value)
        except ValueError:
            raise SchemaViolation(f"'{key}' must be a float, got: {value!r}")
    elif t == "boolean":
        if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
            raise SchemaViolation(f"'{key}' must be a boolean, got: {value!r}")
    elif t == "url":
        if not _URL_RE.match(value):
            raise SchemaViolation(f"'{key}' must be a valid URL, got: {value!r}")
    elif t == "email":
        if not _EMAIL_RE.match(value):
            raise SchemaViolation(f"'{key}' must be a valid email, got: {value!r}")

    if schema.pattern:
        if not re.fullmatch(schema.pattern, value):
            raise SchemaViolation(f"'{key}' does not match pattern {schema.pattern!r}, got: {value!r}")


def validate_all(vault_path: str, password: str) -> list[tuple[str, str]]:
    """Validate all vars in the vault against their schemas. Returns list of (key, error) tuples."""
    data = load_vault(vault_path, password)
    schemas = data.get(SCHEMA_KEY, {})
    errors = []
    for key, entry in schemas.items():
        if entry.get("required") and key not in data:
            errors.append((key, f"'{key}' is required but not set"))
            continue
        if key in data:
            try:
                validate_var(vault_path, password, key, data[key])
            except SchemaViolation as e:
                errors.append((key, str(e)))
    return errors
