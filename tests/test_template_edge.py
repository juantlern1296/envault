"""Edge-case tests for envault.template."""

import pytest

from envault.vault import save_vault
from envault.template import render_string, _PATTERN


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "pw", {"FOO": "bar", "EMPTY": ""})
    return path


def test_empty_value_substituted(vault_file):
    result = render_string("x={{ EMPTY }}y", vault_file, "pw")
    assert result == "x=y"


def test_multiple_same_placeholder_all_replaced(vault_file):
    result = render_string("{{ FOO }}-{{ FOO }}", vault_file, "pw")
    assert result == "bar-bar"


def test_whitespace_variants_in_placeholder(vault_file):
    # Both {{FOO}} and {{ FOO }} and {{  FOO  }} should match
    result = render_string("{{FOO}} and {{  FOO  }}", vault_file, "pw")
    assert result == "bar and bar"


def test_pattern_does_not_match_empty_braces(vault_file):
    result = render_string("{{}")
    assert result == "{{}}"  # no match, left unchanged


def test_render_string_returns_str(vault_file):
    result = render_string("{{ FOO }}", vault_file, "pw")
    assert isinstance(result, str)


def test_multiple_missing_keys_listed(vault_file):
    with pytest.raises(KeyError) as exc_info:
        render_string("{{ MISSING1 }} {{ MISSING2 }}", vault_file, "pw")
    msg = str(exc_info.value)
    assert "MISSING1" in msg
    assert "MISSING2" in msg
