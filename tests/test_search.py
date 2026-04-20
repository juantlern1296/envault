"""Tests for envault.search."""
import pytest
from pathlib import Path
from envault.vault import save_vault, set_var
from envault.search import search_vars

PASSWORD = "hunter2"


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.enc"
    save_vault(str(p), PASSWORD, {})
    return str(p)


def _populate(vault_file):
    set_var(vault_file, PASSWORD, "DB_HOST", "localhost")
    set_var(vault_file, PASSWORD, "DB_PORT", "5432")
    set_var(vault_file, PASSWORD, "APP_SECRET", "s3cr3t")
    set_var(vault_file, PASSWORD, "APP_DEBUG", "true")


def test_search_key_exact(vault_file):
    _populate(vault_file)
    results = search_vars(vault_file, PASSWORD, "DB_HOST")
    assert results == {"DB_HOST": "localhost"}


def test_search_key_wildcard(vault_file):
    _populate(vault_file)
    results = search_vars(vault_file, PASSWORD, "DB_*")
    assert set(results.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_key_no_match(vault_file):
    _populate(vault_file)
    results = search_vars(vault_file, PASSWORD, "MISSING_*")
    assert results == {}


def test_search_values(vault_file):
    _populate(vault_file)
    results = search_vars(vault_file, PASSWORD, "*true*", search_values=True)
    assert "APP_DEBUG" in results


def test_search_values_off_by_default(vault_file):
    _populate(vault_file)
    results = search_vars(vault_file, PASSWORD, "*true*", search_values=False)
    assert results == {}


def test_search_empty_vault(vault_file):
    results = search_vars(vault_file, PASSWORD, "*")
    assert results == {}


def test_search_excludes_profile_keys(vault_file):
    from envault.vault import load_vault, save_vault as sv
    data = load_vault(vault_file, PASSWORD)
    data["profile:prod:DB_HOST"] = "prod-host"
    data["DB_HOST"] = "main-host"
    sv(vault_file, PASSWORD, data)
    results = search_vars(vault_file, PASSWORD, "DB_HOST")
    assert results == {"DB_HOST": "main-host"}


def test_search_within_profile(vault_file):
    from envault.profile import set_profile_var
    set_profile_var(vault_file, PASSWORD, "prod", "DB_HOST", "prod-host")
    set_profile_var(vault_file, PASSWORD, "prod", "DB_PORT", "5432")
    results = search_vars(vault_file, PASSWORD, "DB_*", profile="prod")
    assert set(results.keys()) == {"DB_HOST", "DB_PORT"}
