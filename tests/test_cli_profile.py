import pytest
from click.testing import CliRunner
from envault.cli_profile import profile_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path):
    return {
        "ENVAULT_PATH": str(tmp_path / "vault.enc"),
        "ENVAULT_PASSWORD": "secret",
    }


def _run(runner, vault_env, args):
    return runner.invoke(profile_group, args, env=vault_env, catch_exceptions=False)


def test_set_and_get(runner, vault_env):
    result = _run(runner, vault_env, ["set", "dev", "FOO", "bar"])
    assert result.exit_code == 0
    result = _run(runner, vault_env, ["get", "dev", "FOO"])
    assert result.exit_code == 0
    assert "bar" in result.output


def test_get_missing_exits_nonzero(runner, vault_env):
    result = runner.invoke(profile_group, ["get", "dev", "MISSING"], env=vault_env)
    assert result.exit_code != 0


def test_delete(runner, vault_env):
    _run(runner, vault_env, ["set", "dev", "DEL_ME", "val"])
    result = _run(runner, vault_env, ["delete", "dev", "DEL_ME"])
    assert result.exit_code == 0
    result = runner.invoke(profile_group, ["get", "dev", "DEL_ME"], env=vault_env)
    assert result.exit_code != 0


def test_list_profiles(runner, vault_env):
    _run(runner, vault_env, ["set", "dev", "A", "1"])
    _run(runner, vault_env, ["set", "prod", "B", "2"])
    result = _run(runner, vault_env, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_profile_vars(runner, vault_env):
    _run(runner, vault_env, ["set", "staging", "X", "42"])
    result = _run(runner, vault_env, ["list", "staging"])
    assert "X=42" in result.output
