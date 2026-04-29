"""CLI tests for retention commands."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_retention import retention_group
from envault.vault import save_vault, set_var

PASSWORD = "cli-test-pass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path):
    p = tmp_path / "vault.env"
    save_vault(str(p), PASSWORD, {})
    set_var(str(p), PASSWORD, "MY_KEY", "hello")
    return {"ENVAULT_VAULT": str(p), "ENVAULT_PASSWORD": PASSWORD}


def _run(runner, vault_env, *args):
    with patch("envault.cli_retention.get_password", return_value=PASSWORD):
        return runner.invoke(retention_group, list(args), env=vault_env, catch_exceptions=False)


def test_set_and_get(runner, vault_env):
    res = _run(runner, vault_env, "set", "MY_KEY", "14")
    assert res.exit_code == 0
    assert "14 day" in res.output

    res = _run(runner, vault_env, "get", "MY_KEY")
    assert res.exit_code == 0
    assert "14" in res.output


def test_get_no_policy(runner, vault_env):
    res = _run(runner, vault_env, "get", "MY_KEY")
    assert res.exit_code == 0
    assert "No retention policy" in res.output


def test_set_missing_key_exits_nonzero(runner, vault_env):
    res = _run(runner, vault_env, "set", "GHOST", "7")
    assert res.exit_code != 0


def test_remove_policy(runner, vault_env):
    _run(runner, vault_env, "set", "MY_KEY", "5")
    res = _run(runner, vault_env, "remove", "MY_KEY")
    assert res.exit_code == 0
    assert "removed" in res.output


def test_purge_deletes_stale(runner, vault_env):
    vault_path = vault_env["ENVAULT_VAULT"]
    _run(runner, vault_env, "set", "MY_KEY", "1")
    # backdate
    p = Path(vault_path).with_suffix(".retention.json")
    data = json.loads(p.read_text())
    data["MY_KEY"]["last_accessed"] = (
        datetime.now(timezone.utc) - timedelta(days=3)
    ).isoformat()
    p.write_text(json.dumps(data))

    res = _run(runner, vault_env, "purge")
    assert res.exit_code == 0
    assert "MY_KEY" in res.output
    assert "purged" in res.output


def test_purge_nothing_to_purge(runner, vault_env):
    res = _run(runner, vault_env, "purge")
    assert res.exit_code == 0
    assert "Nothing to purge" in res.output
