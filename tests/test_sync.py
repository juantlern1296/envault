"""Tests for envault.sync module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.sync import push, pull, FileBackend


@pytest.fixture
def vault_file(tmp_path):
    f = tmp_path / "envault.vault"
    f.write_bytes(b"encrypted-data-here")
    return f


@pytest.fixture
def remote_dir(tmp_path):
    return tmp_path / "remote"


def test_file_backend_upload(vault_file, remote_dir):
    dest = remote_dir / "envault.vault"
    backend = FileBackend(str(dest))
    backend.upload(vault_file)
    assert dest.exists()
    assert dest.read_bytes() == b"encrypted-data-here"


def test_file_backend_download(vault_file, tmp_path):
    local = tmp_path / "sub" / "local.vault"
    backend = FileBackend(str(vault_file))
    result = backend.download(local)
    assert result is True
    assert local.read_bytes() == b"encrypted-data-here"


def test_file_backend_download_missing(tmp_path):
    local = tmp_path / "local.vault"
    backend = FileBackend(str(tmp_path / "nonexistent.vault"))
    result = backend.download(local)
    assert result is False
    assert not local.exists()


def test_file_backend_exists(vault_file, tmp_path):
    assert FileBackend(str(vault_file)).exists() is True
    assert FileBackend(str(tmp_path / "nope.vault")).exists() is False


def test_push_uses_file_backend(vault_file, remote_dir):
    dest = remote_dir / "envault.vault"
    push(vault_file, str(dest))
    assert dest.read_bytes() == vault_file.read_bytes()


def test_pull_returns_true_when_remote_exists(vault_file, tmp_path):
    local = tmp_path / "pulled.vault"
    result = pull(local, str(vault_file))
    assert result is True
    assert local.read_bytes() == b"encrypted-data-here"


def test_pull_returns_false_when_remote_missing(tmp_path):
    local = tmp_path / "pulled.vault"
    result = pull(local, str(tmp_path / "ghost.vault"))
    assert result is False


def test_s3_backend_raises_without_boto3(vault_file):
    from envault.sync import S3Backend
    backend = S3Backend("s3://mybucket/myvault")
    with patch.dict("sys.modules", {"boto3": None}):
        with pytest.raises(RuntimeError, match="boto3"):
            backend.upload(vault_file)
