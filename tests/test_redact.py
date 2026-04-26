"""Tests for envault.redact."""

import pytest

from envault.redact import (
    DEFAULT_MASK,
    PARTIAL_VISIBLE,
    _key_is_sensitive,
    redact_value,
    redact_dict,
    redact_vault,
)
from envault.vault import save_vault


# ---------------------------------------------------------------------------
# _key_is_sensitive
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "PASSWORD", "password", "DB_PASSWORD",
    "SECRET", "MY_SECRET_KEY",
    "API_KEY", "api-key", "APIKEY",
    "TOKEN", "ACCESS_TOKEN",
    "PRIVATE_KEY", "private-key",
])
def test_sensitive_keys_detected(key):
    assert _key_is_sensitive(key) is True


@pytest.mark.parametrize("key", [
    "DATABASE_URL", "HOST", "PORT", "DEBUG", "APP_NAME",
])
def test_non_sensitive_keys_not_detected(key):
    assert _key_is_sensitive(key) is False


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_non_sensitive_value_returned_unchanged():
    assert redact_value("HOST", "localhost") == "localhost"


def test_sensitive_value_fully_masked():
    result = redact_value("API_KEY", "super-secret-123")
    assert result == DEFAULT_MASK


def test_partial_mode_reveals_suffix():
    value = "super-secret-abcd"
    result = redact_value("TOKEN", value, partial=True)
    assert result.endswith(value[-PARTIAL_VISIBLE:])
    assert result.startswith(DEFAULT_MASK)


def test_partial_mode_short_value_fully_masked():
    short = "abc"  # shorter than PARTIAL_VISIBLE
    result = redact_value("PASSWORD", short, partial=True)
    assert result == DEFAULT_MASK


def test_custom_mask():
    result = redact_value("SECRET", "mysecret", mask="[HIDDEN]")
    assert result == "[HIDDEN]"


# ---------------------------------------------------------------------------
# redact_dict
# ---------------------------------------------------------------------------

def test_redact_dict_masks_sensitive_keys():
    data = {"API_KEY": "abc123", "HOST": "example.com"}
    result = redact_dict(data)
    assert result["API_KEY"] == DEFAULT_MASK
    assert result["HOST"] == "example.com"


def test_redact_dict_does_not_mutate_input():
    data = {"PASSWORD": "secret"}
    redact_dict(data)
    assert data["PASSWORD"] == "secret"


# ---------------------------------------------------------------------------
# redact_vault
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "pass", {"API_KEY": "topsecret", "APP_ENV": "production"})
    return path


def test_redact_vault_masks_sensitive(vault_file):
    result = redact_vault(vault_file, "pass")
    assert result["API_KEY"] == DEFAULT_MASK
    assert result["APP_ENV"] == "production"


def test_redact_vault_partial_mode(vault_file):
    result = redact_vault(vault_file, "pass", partial=True)
    assert result["API_KEY"].endswith("cret")
    assert result["API_KEY"].startswith(DEFAULT_MASK)
