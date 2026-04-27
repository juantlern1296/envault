"""Tests for envault.promote."""
from __future__ import annotations

import pytest

from envault.promote import PromoteError, promote_all, promote_var
from envault.vault import load_vault, save_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "pw", {})
    return path


def _set(vault_file, key, value, password="pw"):
    data = load_vault(vault_file, password)
    data[key] = value
    save_vault(vault_file, password, data)


# ---------------------------------------------------------------------------
# promote_var
# ---------------------------------------------------------------------------

def test_promote_var_copies_value(vault_file):
    _set(vault_file, "staging:DB_URL", "postgres://staging")
    result = promote_var(vault_file, "pw", "DB_URL", "staging", "prod")
    assert "DB_URL" in result.promoted
    data = load_vault(vault_file, "pw")
    assert data["prod:DB_URL"] == "postgres://staging"


def test_promote_var_missing_key_raises(vault_file):
    with pytest.raises(PromoteError, match="not found"):
        promote_var(vault_file, "pw", "MISSING", "staging", "prod")


def test_promote_var_skips_existing_without_overwrite(vault_file):
    _set(vault_file, "staging:SECRET", "s_val")
    _set(vault_file, "prod:SECRET", "p_val")
    result = promote_var(vault_file, "pw", "SECRET", "staging", "prod", overwrite=False)
    assert "SECRET" in result.skipped
    data = load_vault(vault_file, "pw")
    assert data["prod:SECRET"] == "p_val"  # unchanged


def test_promote_var_overwrites_when_flag_set(vault_file):
    _set(vault_file, "staging:SECRET", "new_val")
    _set(vault_file, "prod:SECRET", "old_val")
    result = promote_var(vault_file, "pw", "SECRET", "staging", "prod", overwrite=True)
    assert "SECRET" in result.overwritten
    data = load_vault(vault_file, "pw")
    assert data["prod:SECRET"] == "new_val"


# ---------------------------------------------------------------------------
# promote_all
# ---------------------------------------------------------------------------

def test_promote_all_copies_all_keys(vault_file):
    _set(vault_file, "staging:A", "1")
    _set(vault_file, "staging:B", "2")
    result = promote_all(vault_file, "pw", "staging", "prod")
    assert set(result.promoted) == {"A", "B"}
    data = load_vault(vault_file, "pw")
    assert data["prod:A"] == "1"
    assert data["prod:B"] == "2"


def test_promote_all_empty_namespace_returns_empty_result(vault_file):
    result = promote_all(vault_file, "pw", "staging", "prod")
    assert result.promoted == []
    assert result.skipped == []


def test_promote_all_with_key_filter(vault_file):
    _set(vault_file, "staging:A", "1")
    _set(vault_file, "staging:B", "2")
    _set(vault_file, "staging:C", "3")
    result = promote_all(vault_file, "pw", "staging", "prod", keys=["A", "C"])
    assert set(result.promoted) == {"A", "C"}
    data = load_vault(vault_file, "pw")
    assert "prod:B" not in data


def test_promote_all_skips_and_overwrites_mixed(vault_file):
    _set(vault_file, "staging:X", "new_x")
    _set(vault_file, "staging:Y", "new_y")
    _set(vault_file, "prod:X", "old_x")  # already exists
    result = promote_all(vault_file, "pw", "staging", "prod", overwrite=False)
    assert "X" in result.skipped
    assert "Y" in result.promoted
