import pytest
from pathlib import Path
from envault.profile import (
    set_profile_var,
    get_profile_var,
    delete_profile_var,
    list_profiles,
    list_profile_vars,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_and_get(vault_file):
    set_profile_var(vault_file, PASSWORD, "dev", "DB_URL", "sqlite://")
    assert get_profile_var(vault_file, PASSWORD, "dev", "DB_URL") == "sqlite://"


def test_get_missing_key_raises(vault_file):
    with pytest.raises(KeyError, match="DB_URL"):
        get_profile_var(vault_file, PASSWORD, "dev", "DB_URL")


def test_delete_var(vault_file):
    set_profile_var(vault_file, PASSWORD, "dev", "API_KEY", "abc")
    delete_profile_var(vault_file, PASSWORD, "dev", "API_KEY")
    with pytest.raises(KeyError):
        get_profile_var(vault_file, PASSWORD, "dev", "API_KEY")


def test_delete_missing_raises(vault_file):
    with pytest.raises(KeyError):
        delete_profile_var(vault_file, PASSWORD, "dev", "NOPE")


def test_list_profiles(vault_file):
    set_profile_var(vault_file, PASSWORD, "dev", "X", "1")
    set_profile_var(vault_file, PASSWORD, "prod", "Y", "2")
    profiles = list_profiles(vault_file, PASSWORD)
    assert "dev" in profiles
    assert "prod" in profiles


def test_list_profile_vars(vault_file):
    set_profile_var(vault_file, PASSWORD, "staging", "FOO", "bar")
    set_profile_var(vault_file, PASSWORD, "staging", "BAZ", "qux")
    vars_ = list_profile_vars(vault_file, PASSWORD, "staging")
    assert vars_ == {"FOO": "bar", "BAZ": "qux"}


def test_profiles_isolated(vault_file):
    set_profile_var(vault_file, PASSWORD, "dev", "KEY", "dev_val")
    set_profile_var(vault_file, PASSWORD, "prod", "KEY", "prod_val")
    assert get_profile_var(vault_file, PASSWORD, "dev", "KEY") == "dev_val"
    assert get_profile_var(vault_file, PASSWORD, "prod", "KEY") == "prod_val"
