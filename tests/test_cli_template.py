"""CLI tests for the template render commands."""

import os
import pytest
from click.testing import CliRunner

from envault.cli_template import template_group
from envault.vault import save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path):
    vault_path = str(tmp_path / "vault.enc")
    save_vault(vault_path, "pw", {"HOST": "db.local", "PORT": "3306"})
    env = {"ENVAULT_PATH": vault_path, "ENVAULT_PASSWORD": "pw"}
    return vault_path, tmp_path, env


def _run(runner, env, *args):
    return runner.invoke(template_group, list(args), env=env)


def test_echo_basic(runner, vault_env):
    _, _, env = vault_env
    result = _run(runner, env, "echo", "host={{ HOST }} port={{ PORT }}")
    assert result.exit_code == 0
    assert "db.local" in result.output
    assert "3306" in result.output


def test_echo_missing_key_exits_nonzero(runner, vault_env):
    _, _, env = vault_env
    result = _run(runner, env, "echo", "{{ MISSING }}")
    assert result.exit_code != 0


def test_render_file(runner, vault_env, tmp_path):
    vault_path, _, env = vault_env
    src = tmp_path / "tmpl.conf"
    dst = tmp_path / "out.conf"
    src.write_text("host={{ HOST }}\nport={{ PORT }}\n")

    result = _run(runner, env, "render", str(src), str(dst))
    assert result.exit_code == 0
    assert dst.read_text() == "host=db.local\nport=3306\n"
    assert "2 variable(s)" in result.output


def test_render_file_strict_missing_exits_nonzero(runner, vault_env, tmp_path):
    vault_path, _, env = vault_env
    src = tmp_path / "tmpl.conf"
    dst = tmp_path / "out.conf"
    src.write_text("{{ HOST }} {{ UNDEFINED }}")

    result = _run(runner, env, "render", str(src), str(dst))
    assert result.exit_code != 0


def test_render_file_no_strict(runner, vault_env, tmp_path):
    vault_path, _, env = vault_env
    src = tmp_path / "tmpl.conf"
    dst = tmp_path / "out.conf"
    src.write_text("{{ HOST }} {{ UNDEFINED }}")

    result = _run(runner, env, "render", str(src), str(dst), "--no-strict")
    assert result.exit_code == 0
    content = dst.read_text()
    assert "db.local" in content
    assert "{{ UNDEFINED }}" in content
