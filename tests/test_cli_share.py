import pytest
from click.testing import CliRunner
from envault.cli_share import share_group
from envault.vault import set_var, get_var
import os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path):
    vpath = str(tmp_path / "vault.json")
    return {"ENVAULT_PATH": vpath, "ENVAULT_PASSWORD": "testpass", "_path": vpath}


def _run(runner, vault_env, args, input_text=None):
    env = {k: v for k, v in vault_env.items() if not k.startswith("_")}
    return runner.invoke(share_group, args, input=input_text, env=env)


def test_create_and_import(runner, vault_env, tmp_path):
    vpath = vault_env["_path"]
    set_var(vpath, "testpass", "SECRET", "topsecret")

    result = _run(runner, vault_env, ["create", "SECRET"], input_text="sharepass\nsharepass\n")
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    token = lines[-1]

    dest = str(tmp_path / "dest.json")
    dest_env = {"ENVAULT_PATH": dest, "ENVAULT_PASSWORD": "testpass"}
    result2 = runner.invoke(share_group, ["import", token], input=f"sharepass\n", env=dest_env)
    assert result2.exit_code == 0
    assert "SECRET" in result2.output
    assert get_var(dest, "testpass", "SECRET") == "topsecret"


def test_create_missing_key_exits_nonzero(runner, vault_env):
    result = _run(runner, vault_env, ["create", "NOTEXIST"], input_text="sharepass\nsharepass\n")
    assert result.exit_code != 0


def test_import_bad_token_exits_nonzero(runner, vault_env):
    result = _run(runner, vault_env, ["import", "badtoken"], input_text="sharepass\n")
    assert result.exit_code != 0
