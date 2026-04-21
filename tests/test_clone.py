import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import save_vault, load_vault
from envault.clone import clone_var, clone_all, CloneError
from envault.cli_clone import clone_group

PASSWORD = "test-secret"


@pytest.fixture
def src_vault(tmp_path):
    p = tmp_path / "src.vault"
    save_vault(p, PASSWORD, {"API_KEY": "abc123", "DB_URL": "postgres://localhost"})
    return p


@pytest.fixture
def dst_vault(tmp_path):
    return tmp_path / "dst.vault"


def test_clone_var_copies_value(src_vault, dst_vault):
    clone_var(str(src_vault), PASSWORD, str(dst_vault), PASSWORD, "API_KEY")
    data = load_vault(dst_vault, PASSWORD)
    assert data["API_KEY"] == "abc123"


def test_clone_var_with_rename(src_vault, dst_vault):
    clone_var(str(src_vault), PASSWORD, str(dst_vault), PASSWORD, "API_KEY", dest_key="MY_KEY")
    data = load_vault(dst_vault, PASSWORD)
    assert "MY_KEY" in data
    assert "API_KEY" not in data


def test_clone_var_missing_key_raises(src_vault, dst_vault):
    with pytest.raises(CloneError, match="not found"):
        clone_var(str(src_vault), PASSWORD, str(dst_vault), PASSWORD, "NONEXISTENT")


def test_clone_var_no_overwrite_raises(src_vault, dst_vault):
    clone_var(str(src_vault), PASSWORD, str(dst_vault), PASSWORD, "API_KEY")
    with pytest.raises(CloneError, match="already exists"):
        clone_var(str(src_vault), PASSWORD, str(dst_vault), PASSWORD, "API_KEY")


def test_clone_var_overwrite_succeeds(src_vault, dst_vault):
    save_vault(dst_vault, PASSWORD, {"API_KEY": "old"})
    clone_var(str(src_vault), PASSWORD, str(dst_vault), PASSWORD, "API_KEY", overwrite=True)
    data = load_vault(dst_vault, PASSWORD)
    assert data["API_KEY"] == "abc123"


def test_clone_all_copies_all_keys(src_vault, dst_vault):
    results = clone_all(str(src_vault), PASSWORD, str(dst_vault), PASSWORD)
    assert results == {"API_KEY": "ok", "DB_URL": "ok"}
    data = load_vault(dst_vault, PASSWORD)
    assert data["API_KEY"] == "abc123"
    assert data["DB_URL"] == "postgres://localhost"


def test_clone_all_skips_existing_without_overwrite(src_vault, dst_vault):
    save_vault(dst_vault, PASSWORD, {"API_KEY": "old"})
    results = clone_all(str(src_vault), PASSWORD, str(dst_vault), PASSWORD)
    assert results["API_KEY"] == "skipped"
    assert results["DB_URL"] == "ok"
    data = load_vault(dst_vault, PASSWORD)
    assert data["API_KEY"] == "old"  # unchanged


def test_clone_all_overwrite_replaces_existing(src_vault, dst_vault):
    save_vault(dst_vault, PASSWORD, {"API_KEY": "old"})
    results = clone_all(str(src_vault), PASSWORD, str(dst_vault), PASSWORD, overwrite=True)
    assert results["API_KEY"] == "ok"
    data = load_vault(dst_vault, PASSWORD)
    assert data["API_KEY"] == "abc123"


def test_cli_clone_var(src_vault, dst_vault):
    runner = CliRunner()
    result = runner.invoke(
        clone_group,
        ["var", "API_KEY", "--src", str(src_vault), "--src-pass", PASSWORD,
         "--dst", str(dst_vault), "--dst-pass", PASSWORD],
    )
    assert result.exit_code == 0
    assert "Cloned" in result.output


def test_cli_clone_all(src_vault, dst_vault):
    runner = CliRunner()
    result = runner.invoke(
        clone_group,
        ["all", "--src", str(src_vault), "--src-pass", PASSWORD,
         "--dst", str(dst_vault), "--dst-pass", PASSWORD],
    )
    assert result.exit_code == 0
    assert "copied" in result.output
