"""Tests for envault.label."""
import pytest

from envault.vault import save_vault
from envault.label import (
    LabelError,
    set_label,
    remove_label,
    get_labels,
    find_by_label,
)

PASSWORD = "test-pass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, PASSWORD, {"DB_HOST": "localhost", "API_KEY": "secret"})
    return path


def test_set_label_creates_entry(vault_file):
    set_label(vault_file, PASSWORD, "DB_HOST", "env", "production")
    labels = get_labels(vault_file, PASSWORD, "DB_HOST")
    assert labels == {"env": "production"}


def test_set_multiple_labels_on_same_key(vault_file):
    set_label(vault_file, PASSWORD, "API_KEY", "env", "staging")
    set_label(vault_file, PASSWORD, "API_KEY", "owner", "team-a")
    labels = get_labels(vault_file, PASSWORD, "API_KEY")
    assert labels["env"] == "staging"
    assert labels["owner"] == "team-a"


def test_set_label_missing_key_raises(vault_file):
    with pytest.raises(LabelError, match="not found in vault"):
        set_label(vault_file, PASSWORD, "MISSING", "env", "prod")


def test_get_labels_no_labels_returns_empty(vault_file):
    assert get_labels(vault_file, PASSWORD, "DB_HOST") == {}


def test_remove_label(vault_file):
    set_label(vault_file, PASSWORD, "DB_HOST", "env", "production")
    remove_label(vault_file, PASSWORD, "DB_HOST", "env")
    assert get_labels(vault_file, PASSWORD, "DB_HOST") == {}


def test_remove_label_missing_raises(vault_file):
    with pytest.raises(LabelError, match="not found on key"):
        remove_label(vault_file, PASSWORD, "DB_HOST", "nonexistent")


def test_find_by_label_returns_matching_keys(vault_file):
    set_label(vault_file, PASSWORD, "DB_HOST", "env", "production")
    set_label(vault_file, PASSWORD, "API_KEY", "env", "production")
    keys = find_by_label(vault_file, PASSWORD, "env")
    assert set(keys) == {"DB_HOST", "API_KEY"}


def test_find_by_label_with_value_filter(vault_file):
    set_label(vault_file, PASSWORD, "DB_HOST", "env", "production")
    set_label(vault_file, PASSWORD, "API_KEY", "env", "staging")
    keys = find_by_label(vault_file, PASSWORD, "env", value="production")
    assert keys == ["DB_HOST"]


def test_find_by_label_no_match_returns_empty(vault_file):
    assert find_by_label(vault_file, PASSWORD, "env") == []


def test_overwrite_label_value(vault_file):
    set_label(vault_file, PASSWORD, "DB_HOST", "env", "staging")
    set_label(vault_file, PASSWORD, "DB_HOST", "env", "production")
    labels = get_labels(vault_file, PASSWORD, "DB_HOST")
    assert labels["env"] == "production"
