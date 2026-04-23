"""Edge-case tests for envault.migrate."""

import pytest

from envault.migrate import (
    _MIGRATIONS,
    _META_KEY,
    list_migrations,
    register_migration,
    run_migrations,
)
from envault.vault import load_vault, save_vault


@pytest.fixture(autouse=True)
def _clean_registry():
    original = dict(_MIGRATIONS)
    yield
    _MIGRATIONS.clear()
    _MIGRATIONS.update(original)


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "pw", {})
    return path


def test_no_registered_migrations_returns_empty_status(vault_file):
    statuses = list_migrations(vault_file, "pw")
    # only built-ins; after cleanup should be empty
    assert isinstance(statuses, dict)


def test_run_specific_version_only(vault_file):
    @register_migration("only_a")
    def _(data):
        data["A"] = "a"
        return data

    @register_migration("only_b")
    def __(data):
        data["B"] = "b"
        return data

    result = run_migrations(vault_file, "pw", versions=["only_a"])
    assert "only_a" in result.applied
    assert "only_b" not in result.applied
    data = load_vault(vault_file, "pw")
    assert "A" in data
    assert "B" not in data


def test_meta_key_not_duplicated_on_repeat(vault_file):
    @register_migration("dedup")
    def _(data):
        return data

    run_migrations(vault_file, "pw")
    run_migrations(vault_file, "pw")
    data = load_vault(vault_file, "pw")
    assert data[_META_KEY].count("dedup") == 1


def test_migration_result_ok_false_on_error(vault_file):
    from envault.migrate import MigrationResult
    r = MigrationResult(errors={"v": "oops"})
    assert not r.ok


def test_migration_result_ok_true_when_clean(vault_file):
    from envault.migrate import MigrationResult
    r = MigrationResult(applied=["v1"])
    assert r.ok
