"""Tests for envault.migrate."""

import pytest

from envault.migrate import (
    MigrationResult,
    _MIGRATIONS,
    _META_KEY,
    list_migrations,
    register_migration,
    run_migrations,
)
from envault.vault import load_vault, save_vault


@pytest.fixture(autouse=True)
def _clean_registry():
    """Isolate registry between tests."""
    original = dict(_MIGRATIONS)
    yield
    _MIGRATIONS.clear()
    _MIGRATIONS.update(original)


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "pw", {})
    return path


def test_run_applies_migration(vault_file):
    @register_migration("v1")
    def _(data):
        data["MIGRATED"] = "yes"
        return data

    result = run_migrations(vault_file, "pw")
    assert "v1" in result.applied
    assert result.ok
    data = load_vault(vault_file, "pw")
    assert data["MIGRATED"] == "yes"


def test_run_skips_already_applied(vault_file):
    @register_migration("v2")
    def _(data):
        data["X"] = "1"
        return data

    run_migrations(vault_file, "pw")
    result = run_migrations(vault_file, "pw")
    assert "v2" in result.skipped
    assert result.applied == []


def test_run_records_meta_key(vault_file):
    @register_migration("v3")
    def _(data):
        return data

    run_migrations(vault_file, "pw")
    data = load_vault(vault_file, "pw")
    assert "v3" in data[_META_KEY]


def test_run_unknown_version_records_error(vault_file):
    result = run_migrations(vault_file, "pw", versions=["nonexistent"])
    assert "nonexistent" in result.errors
    assert not result.ok


def test_list_migrations_shows_pending_and_applied(vault_file):
    @register_migration("v4")
    def _(data):
        return data

    statuses = list_migrations(vault_file, "pw")
    assert statuses["v4"] == "pending"

    run_migrations(vault_file, "pw")
    statuses = list_migrations(vault_file, "pw")
    assert statuses["v4"] == "applied"


def test_migration_exception_stops_chain_and_records_error(vault_file):
    @register_migration("e1")
    def _(data):
        raise ValueError("boom")

    @register_migration("e2")
    def __(data):
        data["SHOULD_NOT"] = "appear"
        return data

    result = run_migrations(vault_file, "pw")
    assert "e1" in result.errors
    data = load_vault(vault_file, "pw")
    assert "SHOULD_NOT" not in data
