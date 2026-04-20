"""Lint vault variables for common issues."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from envault.vault import load_vault


@dataclass
class LintIssue:
    key: str
    severity: str  # 'warning' | 'error'
    message: str


_VALID_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_EMPTY_VALUE_RE = re.compile(r'^\s*$')
_SECRET_HINTS = ('password', 'secret', 'token', 'key', 'api', 'auth', 'private')


def _check_key_naming(key: str) -> LintIssue | None:
    if not _VALID_KEY_RE.match(key):
        return LintIssue(
            key=key,
            severity='warning',
            message=f"Key '{key}' does not follow UPPER_SNAKE_CASE convention",
        )
    return None


def _check_empty_value(key: str, value: str) -> LintIssue | None:
    if _EMPTY_VALUE_RE.match(value):
        return LintIssue(
            key=key,
            severity='warning',
            message=f"Key '{key}' has an empty or whitespace-only value",
        )
    return None


def _check_plaintext_secret(key: str, value: str) -> LintIssue | None:
    lower_key = key.lower()
    if any(hint in lower_key for hint in _SECRET_HINTS):
        if len(value) < 16:
            return LintIssue(
                key=key,
                severity='warning',
                message=(
                    f"Key '{key}' looks like a secret but its value is very short "
                    f"(< 16 chars); consider a stronger value"
                ),
            )
    return None


def lint_vault(vault_path: str, password: str) -> List[LintIssue]:
    """Run all lint checks on the vault and return a list of issues."""
    data = load_vault(vault_path, password)
    issues: List[LintIssue] = []

    for key, value in data.items():
        for check in (_check_key_naming, _check_empty_value, _check_plaintext_secret):
            if check == _check_empty_value:
                issue = check(key, value)
            elif check == _check_plaintext_secret:
                issue = check(key, value)
            else:
                issue = check(key)
            if issue:
                issues.append(issue)

    issues.sort(key=lambda i: (i.severity, i.key))
    return issues
