"""Tests for envault.schema."""
import pytest
from click.testing import CliRunner

from envault.vault import save_vault
from envault.schema import (
    SchemaViolation,
    delete_schema,
    get_schema,
    set_schema,
    validate_all,
    validate_var,
)

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.env")
    save_vault(path, PASSWORD, {})
    return path


def test_set_and_get_schema(vault_file):
    set_schema(vault_file, PASSWORD, "PORT", type="integer", required=True, description="Server port")
    entry = get_schema(vault_file, PASSWORD, "PORT")
    assert entry is not None
    assert entry.type == "integer"
    assert entry.required is True
    assert entry.description == "Server port"


def test_get_missing_schema_returns_none(vault_file):
    assert get_schema(vault_file, PASSWORD, "NONEXISTENT") is None


def test_delete_schema(vault_file):
    set_schema(vault_file, PASSWORD, "FOO")
    delete_schema(vault_file, PASSWORD, "FOO")
    assert get_schema(vault_file, PASSWORD, "FOO") is None


def test_delete_missing_schema_raises(vault_file):
    with pytest.raises(KeyError):
        delete_schema(vault_file, PASSWORD, "MISSING")


def test_set_schema_invalid_type_raises(vault_file):
    with pytest.raises(ValueError, match="Invalid type"):
        set_schema(vault_file, PASSWORD, "X", type="blob")


def test_validate_integer_ok(vault_file):
    set_schema(vault_file, PASSWORD, "PORT", type="integer")
    validate_var(vault_file, PASSWORD, "PORT", "8080")  # no exception


def test_validate_integer_fails(vault_file):
    set_schema(vault_file, PASSWORD, "PORT", type="integer")
    with pytest.raises(SchemaViolation, match="integer"):
        validate_var(vault_file, PASSWORD, "PORT", "not-a-number")


def test_validate_boolean_ok(vault_file):
    set_schema(vault_file, PASSWORD, "FLAG", type="boolean")
    for val in ("true", "false", "1", "0", "yes", "no", "True", "FALSE"):
        validate_var(vault_file, PASSWORD, "FLAG", val)


def test_validate_boolean_fails(vault_file):
    set_schema(vault_file, PASSWORD, "FLAG", type="boolean")
    with pytest.raises(SchemaViolation, match="boolean"):
        validate_var(vault_file, PASSWORD, "FLAG", "maybe")


def test_validate_url_ok(vault_file):
    set_schema(vault_file, PASSWORD, "ENDPOINT", type="url")
    validate_var(vault_file, PASSWORD, "ENDPOINT", "https://example.com/path")


def test_validate_url_fails(vault_file):
    set_schema(vault_file, PASSWORD, "ENDPOINT", type="url")
    with pytest.raises(SchemaViolation, match="URL"):
        validate_var(vault_file, PASSWORD, "ENDPOINT", "not-a-url")


def test_validate_email_ok(vault_file):
    set_schema(vault_file, PASSWORD, "CONTACT", type="email")
    validate_var(vault_file, PASSWORD, "CONTACT", "user@example.com")


def test_validate_email_fails(vault_file):
    set_schema(vault_file, PASSWORD, "CONTACT", type="email")
    with pytest.raises(SchemaViolation, match="email"):
        validate_var(vault_file, PASSWORD, "CONTACT", "not-an-email")


def test_validate_pattern_ok(vault_file):
    set_schema(vault_file, PASSWORD, "CODE", pattern=r"[A-Z]{3}-\d{4}")
    validate_var(vault_file, PASSWORD, "CODE", "ABC-1234")


def test_validate_pattern_fails(vault_file):
    set_schema(vault_file, PASSWORD, "CODE", pattern=r"[A-Z]{3}-\d{4}")
    with pytest.raises(SchemaViolation, match="pattern"):
        validate_var(vault_file, PASSWORD, "CODE", "abc-1234")


def test_validate_no_schema_is_ok(vault_file):
    # variable with no schema should always pass
    validate_var(vault_file, PASSWORD, "ANYTHING", "whatever")


def test_validate_all_required_missing(vault_file):
    set_schema(vault_file, PASSWORD, "MUST_EXIST", required=True)
    errors = validate_all(vault_file, PASSWORD)
    keys = [k for k, _ in errors]
    assert "MUST_EXIST" in keys


def test_validate_all_clean(vault_file):
    from envault.vault import load_vault, save_vault as sv
    data = {"PORT": "9000"}
    sv(vault_file, PASSWORD, data)
    set_schema(vault_file, PASSWORD, "PORT", type="integer")
    errors = validate_all(vault_file, PASSWORD)
    assert errors == []
