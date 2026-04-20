"""Policy enforcement: define and check rules for vault variable access patterns."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.vault import load_vault


class PolicyViolation(Exception):
    pass


def _policy_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".policy.json")


def _load_policies(vault_file: str) -> dict[str, Any]:
    path = _policy_path(vault_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_policies(vault_file: str, policies: dict[str, Any]) -> None:
    path = _policy_path(vault_file)
    path.write_text(json.dumps(policies, indent=2))


def set_policy(vault_file: str, key: str, rules: dict[str, Any]) -> None:
    """Attach a policy rule-set to a vault key.

    Supported rules:
      - required (bool): key must exist in vault
      - min_length (int): value must be at least this many characters
      - max_length (int): value must be at most this many characters
      - pattern (str): value must match this regex pattern
    """
    policies = _load_policies(vault_file)
    policies[key] = rules
    _save_policies(vault_file, policies)


def get_policy(vault_file: str, key: str) -> dict[str, Any] | None:
    """Return the policy for a key, or None if not set."""
    return _load_policies(vault_file).get(key)


def delete_policy(vault_file: str, key: str) -> None:
    """Remove the policy for a key."""
    policies = _load_policies(vault_file)
    if key not in policies:
        raise KeyError(f"No policy for key: {key}")
    del policies[key]
    _save_policies(vault_file, policies)


def check_policies(vault_file: str, password: str) -> list[str]:
    """Validate all policy rules against the current vault contents.

    Returns a list of violation messages (empty list means all good).
    """
    import re

    policies = _load_policies(vault_file)
    if not policies:
        return []

    data = load_vault(vault_file, password)
    violations: list[str] = []

    for key, rules in policies.items():
        value: str | None = data.get(key)

        if rules.get("required") and value is None:
            violations.append(f"{key}: required but not set")
            continue

        if value is None:
            continue

        min_len = rules.get("min_length")
        if min_len is not None and len(value) < min_len:
            violations.append(f"{key}: value too short (min {min_len})")

        max_len = rules.get("max_length")
        if max_len is not None and len(value) > max_len:
            violations.append(f"{key}: value too long (max {max_len})")

        pattern = rules.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            violations.append(f"{key}: value does not match pattern '{pattern}'")

    return violations
