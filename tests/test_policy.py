"""Tests for envault.policy."""

import pytest

from envault.policy import (
    PolicyViolation,
    check_policies,
    delete_policy,
    get_policy,
    set_policy,
)
from envault.vault import save_vault

PASSWORD = "hunter2"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.env")
    save_vault(path, PASSWORD, {})
    return path


def _populate(vault_file, data):
    save_vault(vault_file, PASSWORD, data)


# --- set / get / delete ---

def test_set_and_get_policy(vault_file):
    set_policy(vault_file, "API_KEY", {"required": True, "min_length": 8})
    policy = get_policy(vault_file, "API_KEY")
    assert policy["required"] is True
    assert policy["min_length"] == 8


def test_get_missing_policy_returns_none(vault_file):
    assert get_policy(vault_file, "NONEXISTENT") is None


def test_delete_policy(vault_file):
    set_policy(vault_file, "FOO", {"required": True})
    delete_policy(vault_file, "FOO")
    assert get_policy(vault_file, "FOO") is None


def test_delete_missing_policy_raises(vault_file):
    with pytest.raises(KeyError):
        delete_policy(vault_file, "MISSING")


# --- check_policies ---

def test_no_policies_returns_empty(vault_file):
    _populate(vault_file, {"X": "y"})
    assert check_policies(vault_file, PASSWORD) == []


def test_required_key_present_passes(vault_file):
    _populate(vault_file, {"TOKEN": "abc"})
    set_policy(vault_file, "TOKEN", {"required": True})
    assert check_policies(vault_file, PASSWORD) == []


def test_required_key_missing_fails(vault_file):
    set_policy(vault_file, "TOKEN", {"required": True})
    violations = check_policies(vault_file, PASSWORD)
    assert any("required" in v for v in violations)


def test_min_length_passes(vault_file):
    _populate(vault_file, {"PW": "longpassword"})
    set_policy(vault_file, "PW", {"min_length": 8})
    assert check_policies(vault_file, PASSWORD) == []


def test_min_length_fails(vault_file):
    _populate(vault_file, {"PW": "short"})
    set_policy(vault_file, "PW", {"min_length": 10})
    violations = check_policies(vault_file, PASSWORD)
    assert any("too short" in v for v in violations)


def test_max_length_fails(vault_file):
    _populate(vault_file, {"NOTE": "this is way too long for the rule"})
    set_policy(vault_file, "NOTE", {"max_length": 5})
    violations = check_policies(vault_file, PASSWORD)
    assert any("too long" in v for v in violations)


def test_pattern_passes(vault_file):
    _populate(vault_file, {"PORT": "8080"})
    set_policy(vault_file, "PORT", {"pattern": r"\d+"})
    assert check_policies(vault_file, PASSWORD) == []


def test_pattern_fails(vault_file):
    _populate(vault_file, {"PORT": "not-a-number"})
    set_policy(vault_file, "PORT", {"pattern": r"\d+"})
    violations = check_policies(vault_file, PASSWORD)
    assert any("pattern" in v for v in violations)


def test_multiple_violations_all_reported(vault_file):
    _populate(vault_file, {"A": "x"})
    set_policy(vault_file, "A", {"min_length": 10, "pattern": r"\d+"})
    violations = check_policies(vault_file, PASSWORD)
    assert len(violations) == 2
