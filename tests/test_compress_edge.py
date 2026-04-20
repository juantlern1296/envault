"""Edge-case tests for envault.compress."""

from pathlib import Path

import pytest

from envault.vault import save_vault
from envault.compress import (
    compress_vault,
    decompress_vault,
    compress_ratio,
    _compress_value,
    _decompress_value,
)


PASSWORD = "edge-pass"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.enc"
    save_vault(path, PASSWORD, {})
    return path


def test_compress_empty_vault_returns_zero(vault_file: Path) -> None:
    count = compress_vault(vault_file, PASSWORD)
    assert count == 0


def test_decompress_empty_vault_returns_zero(vault_file: Path) -> None:
    count = decompress_vault(vault_file, PASSWORD)
    assert count == 0


def test_compress_ratio_empty_vault(vault_file: Path) -> None:
    ratios = compress_ratio(vault_file, PASSWORD)
    assert ratios == {}


def test_compress_value_empty_string() -> None:
    compressed = _compress_value("")
    assert _decompress_value(compressed) == ""


def test_compress_value_unicode() -> None:
    original = "こんにちは世界 🌍"
    compressed = _compress_value(original)
    assert _decompress_value(compressed) == original


def test_compress_value_large_payload() -> None:
    original = "X" * 10_000
    compressed = _compress_value(original)
    decompressed = _decompress_value(compressed)
    assert decompressed == original
    # gzip should actually shrink repetitive data
    assert len(compressed) < len(original)


def test_compress_ratio_less_than_one_for_repetitive_data(vault_file: Path) -> None:
    save_vault(vault_file, PASSWORD, {"BIG": "A" * 5000})
    compress_vault(vault_file, PASSWORD)
    ratios = compress_ratio(vault_file, PASSWORD)
    assert ratios["BIG"] < 1.0
