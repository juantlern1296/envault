"""Tests for envault.transform."""
import pytest

from envault.transform import (
    TransformError,
    apply_pipeline,
    apply_transform,
    list_transforms,
    transform_var,
)
from envault.vault import save_vault, load_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / "vault.enc"
    save_vault(str(path), "pw", {"KEY": "hello world", "B64": "aGVsbG8="})
    return str(path)


def test_list_transforms_returns_known_names():
    names = list_transforms()
    assert "upper" in names
    assert "lower" in names
    assert "strip" in names
    assert "base64encode" in names
    assert "base64decode" in names
    assert "urlencode" in names


def test_apply_transform_upper():
    assert apply_transform("upper", "hello") == "HELLO"


def test_apply_transform_lower():
    assert apply_transform("lower", "HELLO") == "hello"


def test_apply_transform_strip():
    assert apply_transform("strip", "  hi  ") == "hi"


def test_apply_transform_base64_roundtrip():
    encoded = apply_transform("base64encode", "secret")
    assert apply_transform("base64decode", encoded) == "secret"


def test_apply_transform_urlencode():
    result = apply_transform("urlencode", "a b+c")
    assert result == "a%20b%2Bc"


def test_apply_transform_unknown_raises():
    with pytest.raises(TransformError, match="Unknown transform"):
        apply_transform("nonexistent", "value")


def test_apply_pipeline_chained():
    result = apply_pipeline("  Hello  ", ["strip", "upper"])
    assert result == "HELLO"


def test_apply_pipeline_empty_returns_original():
    assert apply_pipeline("unchanged", []) == "unchanged"


def test_transform_var_saves_result(vault_file):
    new_val = transform_var(vault_file, "pw", "KEY", ["upper"])
    assert new_val == "HELLO WORLD"
    data = load_vault(vault_file, "pw")
    assert data["KEY"] == "HELLO WORLD"


def test_transform_var_dry_run_does_not_save(vault_file):
    result = transform_var(vault_file, "pw", "KEY", ["upper"], dry_run=True)
    assert result == "HELLO WORLD"
    data = load_vault(vault_file, "pw")
    assert data["KEY"] == "hello world"  # unchanged


def test_transform_var_missing_key_raises(vault_file):
    with pytest.raises(TransformError, match="not found"):
        transform_var(vault_file, "pw", "MISSING", ["upper"])


def test_transform_var_pipeline_applied_in_order(vault_file):
    result = transform_var(vault_file, "pw", "KEY", ["upper", "strip"], dry_run=True)
    assert result == "HELLO WORLD"
