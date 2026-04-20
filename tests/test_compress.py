"""Unit tests for envault.compress."""

import pytest
from pathlib import Path

from envault.vault import save_vault, load_vault
from envault.compress import (
    compress_vault,
    decompress_vault,
    compress_ratio,
    _compress_value,
    _decompress_value,
    _is_compressed,
)


PASSWORD = "test-password"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.enc"
    save_vault(path, PASSWORD, {})
    return path


def _populate(vault_file: Path, data: dict) -> None:
    save_vault(vault_file, PASSWORD, data)


def test_compress_value_roundtrip() -> None:
    original = "hello world"
    compressed = _compress_value(original)
    assert _is_compressed(compressed)
    assert _decompress_value(compressed) == original


def test_is_compressed_false_for_plain_string() -> None:
    assert not _is_compressed("plain value")


def test_compress_vault_returns_count(vault_file: Path) -> None:
    _populate(vault_file, {"KEY1": "value1", "KEY2": "value2"})
    count = compress_vault(vault_file, PASSWORD)
    assert count == 2


def test_compress_vault_values_are_stored_compressed(vault_file: Path) -> None:
    _populate(vault_file, {"KEY": "my secret value"})
    compress_vault(vault_file, PASSWORD)
    data = load_vault(vault_file, PASSWORD)
    assert _is_compressed(data["KEY"])


def test_compress_then_decompress_roundtrip(vault_file: Path) -> None:
    original = {"KEY": "my secret value", "OTHER": "another"}
    _populate(vault_file, original)
    compress_vault(vault_file, PASSWORD)
    decompress_vault(vault_file, PASSWORD)
    data = load_vault(vault_file, PASSWORD)
    assert data == original


def test_compress_already_compressed_is_skipped(vault_file: Path) -> None:
    _populate(vault_file, {"KEY": "value"})
    compress_vault(vault_file, PASSWORD)
    count = compress_vault(vault_file, PASSWORD)  # second call
    assert count == 0


def test_decompress_returns_count(vault_file: Path) -> None:
    _populate(vault_file, {"A": "aaa", "B": "bbb"})
    compress_vault(vault_file, PASSWORD)
    count = decompress_vault(vault_file, PASSWORD)
    assert count == 2


def test_decompress_plain_values_skipped(vault_file: Path) -> None:
    _populate(vault_file, {"KEY": "plain"})
    count = decompress_vault(vault_file, PASSWORD)
    assert count == 0


def test_compress_ratio_only_compressed_keys(vault_file: Path) -> None:
    _populate(vault_file, {"KEY": "a" * 200})
    compress_vault(vault_file, PASSWORD)
    ratios = compress_ratio(vault_file, PASSWORD)
    assert "KEY" in ratios
    assert 0 < ratios["KEY"] <= 1.0


def test_compress_ratio_empty_when_no_compressed(vault_file: Path) -> None:
    _populate(vault_file, {"KEY": "plain"})
    ratios = compress_ratio(vault_file, PASSWORD)
    assert ratios == {}
