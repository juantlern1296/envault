"""Tests for envault.mask."""
import pytest

from envault.vault import save_vault, set_var
from envault.mask import (
    MaskError,
    mask_var,
    unmask_var,
    is_masked,
    list_masked,
    apply_mask,
)

PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    vf = str(tmp_path / "vault.enc")
    save_vault(vf, PASSWORD, {})
    set_var(vf, PASSWORD, "API_KEY", "abc123")
    set_var(vf, PASSWORD, "DB_PASS", "hunter2")
    set_var(vf, PASSWORD, "PORT", "5432")
    return vf


def test_mask_var_marks_key(vault_file):
    mask_var(vault_file, PASSWORD, "API_KEY")
    assert is_masked(vault_file, "API_KEY") is True


def test_unmask_var_removes_mark(vault_file):
    mask_var(vault_file, PASSWORD, "API_KEY")
    unmask_var(vault_file, "API_KEY")
    assert is_masked(vault_file, "API_KEY") is False


def test_unmask_noop_when_not_masked(vault_file):
    # Should not raise
    unmask_var(vault_file, "PORT")
    assert is_masked(vault_file, "PORT") is False


def test_mask_missing_key_raises(vault_file):
    with pytest.raises(MaskError, match="MISSING"):
        mask_var(vault_file, PASSWORD, "MISSING")


def test_mask_deduplicates(vault_file):
    mask_var(vault_file, PASSWORD, "API_KEY")
    mask_var(vault_file, PASSWORD, "API_KEY")
    assert list_masked(vault_file).count("API_KEY") == 1


def test_list_masked_empty(vault_file):
    assert list_masked(vault_file) == []


def test_list_masked_returns_all(vault_file):
    mask_var(vault_file, PASSWORD, "API_KEY")
    mask_var(vault_file, PASSWORD, "DB_PASS")
    result = list_masked(vault_file)
    assert set(result) == {"API_KEY", "DB_PASS"}


def test_apply_mask_replaces_masked_values(vault_file):
    mask_var(vault_file, PASSWORD, "API_KEY")
    raw = {"API_KEY": "abc123", "PORT": "5432"}
    masked = apply_mask(vault_file, raw)
    assert masked["API_KEY"] == "***"
    assert masked["PORT"] == "5432"


def test_apply_mask_custom_placeholder(vault_file):
    mask_var(vault_file, PASSWORD, "DB_PASS")
    raw = {"DB_PASS": "hunter2", "PORT": "5432"}
    masked = apply_mask(vault_file, raw, placeholder="[REDACTED]")
    assert masked["DB_PASS"] == "[REDACTED]"


def test_apply_mask_no_masked_keys_unchanged(vault_file):
    raw = {"PORT": "5432", "API_KEY": "abc123"}
    result = apply_mask(vault_file, raw)
    assert result == raw
