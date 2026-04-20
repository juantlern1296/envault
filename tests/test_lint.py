"""Tests for envault.lint."""

import os
import pytest

from envault.vault import save_vault
from envault.lint import lint_vault, LintIssue


PASSWORD = "testpassword"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, PASSWORD, {})
    return path


def _populate(vault_file, data):
    save_vault(vault_file, PASSWORD, data)


def test_lint_clean_vault_returns_no_issues(vault_file):
    _populate(vault_file, {"DATABASE_URL": "postgres://localhost/mydb"})
    issues = lint_vault(vault_file, PASSWORD)
    assert issues == []


def test_lint_detects_lowercase_key(vault_file):
    _populate(vault_file, {"database_url": "postgres://localhost/mydb"})
    issues = lint_vault(vault_file, PASSWORD)
    assert any("UPPER_SNAKE_CASE" in i.message for i in issues)
    assert all(i.severity == "warning" for i in issues)


def test_lint_detects_empty_value(vault_file):
    _populate(vault_file, {"MY_VAR": ""})
    issues = lint_vault(vault_file, PASSWORD)
    assert any("empty" in i.message for i in issues)


def test_lint_detects_whitespace_only_value(vault_file):
    _populate(vault_file, {"MY_VAR": "   "})
    issues = lint_vault(vault_file, PASSWORD)
    assert any("empty or whitespace" in i.message for i in issues)


def test_lint_detects_short_secret(vault_file):
    _populate(vault_file, {"API_KEY": "short"})
    issues = lint_vault(vault_file, PASSWORD)
    assert any("secret" in i.message and "API_KEY" in i.message for i in issues)


def test_lint_no_issue_for_long_secret(vault_file):
    _populate(vault_file, {"API_KEY": "a" * 32})
    issues = lint_vault(vault_file, PASSWORD)
    # Should not flag a long secret value
    assert not any("API_KEY" in i.message and "stronger" in i.message for i in issues)


def test_lint_multiple_issues(vault_file):
    _populate(vault_file, {
        "bad-key": "",
        "ANOTHER_TOKEN": "tiny",
        "GOOD_VAR": "good_value_here",
    })
    issues = lint_vault(vault_file, PASSWORD)
    keys_with_issues = {i.key for i in issues}
    assert "bad-key" in keys_with_issues
    assert "ANOTHER_TOKEN" in keys_with_issues
    assert "GOOD_VAR" not in keys_with_issues


def test_lint_returns_lint_issue_instances(vault_file):
    _populate(vault_file, {"bad-key": "value"})
    issues = lint_vault(vault_file, PASSWORD)
    assert all(isinstance(i, LintIssue) for i in issues)


def test_lint_empty_vault_returns_no_issues(vault_file):
    issues = lint_vault(vault_file, PASSWORD)
    assert issues == []
