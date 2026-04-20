import pytest
import os
from envault.vault import save_vault
from envault.tags import tag_var, untag_var, list_tags, vars_for_tag

PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, PASSWORD, {"DB_URL": "postgres://", "API_KEY": "secret"})
    return path


def test_tag_var_creates_tag(vault_file):
    tag_var(vault_file, PASSWORD, "DB_URL", "database")
    tags = list_tags(vault_file, PASSWORD)
    assert "database" in tags
    assert "DB_URL" in tags["database"]


def test_tag_multiple_vars(vault_file):
    tag_var(vault_file, PASSWORD, "DB_URL", "prod")
    tag_var(vault_file, PASSWORD, "API_KEY", "prod")
    result = vars_for_tag(vault_file, PASSWORD, "prod")
    assert set(result) == {"DB_URL", "API_KEY"}


def test_tag_deduplicates(vault_file):
    tag_var(vault_file, PASSWORD, "DB_URL", "database")
    tag_var(vault_file, PASSWORD, "DB_URL", "database")
    result = vars_for_tag(vault_file, PASSWORD, "database")
    assert result.count("DB_URL") == 1


def test_untag_var(vault_file):
    tag_var(vault_file, PASSWORD, "DB_URL", "database")
    untag_var(vault_file, PASSWORD, "DB_URL", "database")
    result = vars_for_tag(vault_file, PASSWORD, "database")
    assert "DB_URL" not in result


def test_untag_removes_empty_tag(vault_file):
    tag_var(vault_file, PASSWORD, "DB_URL", "solo")
    untag_var(vault_file, PASSWORD, "DB_URL", "solo")
    tags = list_tags(vault_file, PASSWORD)
    assert "solo" not in tags


def test_untag_missing_raises(vault_file):
    with pytest.raises(KeyError):
        untag_var(vault_file, PASSWORD, "DB_URL", "nonexistent")


def test_vars_for_missing_tag_returns_empty(vault_file):
    result = vars_for_tag(vault_file, PASSWORD, "ghost")
    assert result == []
