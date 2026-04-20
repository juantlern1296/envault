"""Tests for envault.template."""

import pytest

from envault.vault import save_vault
from envault.template import render_string, render_file


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "secret", {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "abc123"})
    return path


def test_render_string_basic(vault_file):
    result = render_string("host={{ DB_HOST }} port={{ DB_PORT }}", vault_file, "secret")
    assert result == "host=localhost port=5432"


def test_render_string_no_placeholders(vault_file):
    result = render_string("no placeholders here", vault_file, "secret")
    assert result == "no placeholders here"


def test_render_string_missing_key_raises(vault_file):
    with pytest.raises(KeyError, match="MISSING_VAR"):
        render_string("value={{MISSING_VAR}}", vault_file, "secret")


def test_render_string_wrong_password_raises(vault_file):
    with pytest.raises(Exception):
        render_string("{{ DB_HOST }}", vault_file, "wrong")


def test_render_file_creates_output(tmp_path, vault_file):
    src = tmp_path / "template.txt"
    dst = tmp_path / "output.txt"
    src.write_text("DB_HOST={{ DB_HOST }}\nAPI_KEY={{ API_KEY }}\n")

    substituted = render_file(str(src), str(dst), vault_file, "secret")

    assert dst.read_text() == "DB_HOST=localhost\nAPI_KEY=abc123\n"
    assert set(substituted) == {"DB_HOST", "API_KEY"}


def test_render_file_strict_missing_raises(tmp_path, vault_file):
    src = tmp_path / "template.txt"
    dst = tmp_path / "output.txt"
    src.write_text("{{ DB_HOST }} {{ UNDEFINED }}")

    with pytest.raises(KeyError):
        render_file(str(src), str(dst), vault_file, "secret", strict=True)


def test_render_file_non_strict_leaves_placeholder(tmp_path, vault_file):
    src = tmp_path / "template.txt"
    dst = tmp_path / "output.txt"
    src.write_text("{{ DB_HOST }} {{ UNDEFINED }}")

    render_file(str(src), str(dst), vault_file, "secret", strict=False)

    content = dst.read_text()
    assert "localhost" in content
    assert "{{ UNDEFINED }}" in content


def test_render_string_deduplicates_keys_in_return(tmp_path, vault_file):
    src = tmp_path / "t.txt"
    dst = tmp_path / "o.txt"
    src.write_text("{{ DB_HOST }} and {{ DB_HOST }} again")
    substituted = render_file(str(src), str(dst), vault_file, "secret")
    assert substituted.count("DB_HOST") == 1
