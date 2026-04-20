"""Tests for envault.batch module."""
import pytest
from pathlib import Path

from envault.vault import set_var, load_vault
from envault.batch import batch_set, batch_delete, batch_get, BatchResult


PASSWORD = "batchpass"


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    return str(tmp_path / "vault.enc")


def test_batch_set_all_succeed(vault_file):
    result = batch_set(vault_file, PASSWORD, {"A": "1", "B": "2", "C": "3"})
    assert result.ok
    assert set(result.succeeded) == {"A", "B", "C"}
    assert result.failed == {}


def test_batch_set_values_persisted(vault_file):
    batch_set(vault_file, PASSWORD, {"FOO": "bar", "BAZ": "qux"})
    data = load_vault(vault_file, PASSWORD)
    assert data["FOO"] == "bar"
    assert data["BAZ"] == "qux"


def test_batch_delete_removes_keys(vault_file):
    batch_set(vault_file, PASSWORD, {"X": "10", "Y": "20", "Z": "30"})
    result = batch_delete(vault_file, PASSWORD, ["X", "Y"])
    assert result.ok
    assert set(result.succeeded) == {"X", "Y"}
    data = load_vault(vault_file, PASSWORD)
    assert "X" not in data
    assert "Y" not in data
    assert data["Z"] == "30"


def test_batch_delete_missing_key_records_failure(vault_file):
    # vault is empty — deleting a non-existent key should fail gracefully
    result = batch_delete(vault_file, PASSWORD, ["GHOST"])
    assert not result.ok
    assert "GHOST" in result.failed


def test_batch_delete_stop_on_error(vault_file):
    batch_set(vault_file, PASSWORD, {"KEEP": "yes"})
    result = batch_delete(
        vault_file, PASSWORD, ["MISSING", "KEEP"], stop_on_error=True
    )
    # Should stop after first failure; KEEP should NOT have been deleted
    assert "MISSING" in result.failed
    assert "KEEP" not in result.succeeded
    data = load_vault(vault_file, PASSWORD)
    assert data.get("KEEP") == "yes"


def test_batch_get_returns_values(vault_file):
    batch_set(vault_file, PASSWORD, {"M": "hello", "N": "world"})
    values = batch_get(vault_file, PASSWORD, ["M", "N"])
    assert values == {"M": "hello", "N": "world"}


def test_batch_get_missing_key_returns_none(vault_file):
    batch_set(vault_file, PASSWORD, {"PRESENT": "yes"})
    values = batch_get(vault_file, PASSWORD, ["PRESENT", "ABSENT"])
    assert values["PRESENT"] == "yes"
    assert values["ABSENT"] is None


def test_batch_result_ok_false_when_failures():
    r = BatchResult(succeeded=["A"], failed={"B": "err"})
    assert not r.ok


def test_batch_result_ok_true_when_no_failures():
    r = BatchResult(succeeded=["A", "B"], failed={})
    assert r.ok
