"""Tests for envault.verify."""

from __future__ import annotations

import pytest

from envault.vault import save_vault
from envault.verify import verify_vault, summarise_report, VerifyReport


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.env")


def test_verify_empty_vault_returns_empty_report(vault_file):
    save_vault(vault_file, {}, "pass")
    report = verify_vault(vault_file, "pass")
    assert isinstance(report, VerifyReport)
    assert report.results == []
    assert report.success is True


def test_verify_valid_entries_all_pass(vault_file):
    from envault.vault import set_var
    set_var(vault_file, "pass", "KEY1", "value1")
    set_var(vault_file, "pass", "KEY2", "value2")
    report = verify_vault(vault_file, "pass")
    assert report.success is True
    assert len(report.passed) == 2
    assert len(report.failed) == 0


def test_verify_wrong_password_fails(vault_file):
    from envault.vault import set_var
    set_var(vault_file, "pass", "KEY1", "value1")
    report = verify_vault(vault_file, "wrongpass")
    assert report.success is False
    assert len(report.failed) > 0


def test_verify_missing_vault_returns_failure(tmp_path):
    missing = str(tmp_path / "nope.env")
    report = verify_vault(missing, "pass")
    assert report.success is False
    assert report.failed[0].key == "<vault>"


def test_verify_report_passed_and_failed_split(vault_file):
    from envault.vault import set_var
    set_var(vault_file, "pass", "GOOD", "ok")
    report = verify_vault(vault_file, "pass")
    assert all(r.ok for r in report.passed)
    assert all(not r.ok for r in report.failed)


def test_summarise_report_contains_key_names(vault_file):
    from envault.vault import set_var
    set_var(vault_file, "pass", "MY_KEY", "hello")
    report = verify_vault(vault_file, "pass")
    summary = summarise_report(report)
    assert "MY_KEY" in summary
    assert "OK" in summary
    assert "1 checked" in summary


def test_summarise_report_shows_failure_count(vault_file):
    from envault.vault import set_var
    set_var(vault_file, "pass", "KEY", "v")
    report = verify_vault(vault_file, "badpass")
    summary = summarise_report(report)
    assert "failed" in summary
