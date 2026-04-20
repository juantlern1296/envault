import pytest
from envault.export import export_vars, import_vars


SAMPLE = {"DB_URL": "postgres://localhost/db", "SECRET": 'has"quote'}


def test_export_dotenv_basic():
    out = export_vars({"FOO": "bar"}, fmt="dotenv")
    assert 'FOO="bar"' in out


def test_export_dotenv_escapes_quotes():
    out = export_vars({"K": 'say "hi"'}, fmt="dotenv")
    assert 'K="say \\"hi\\""' in out


def test_export_json_basic():
    out = export_vars({"A": "1"}, fmt="json")
    import json
    data = json.loads(out)
    assert data == {"A": "1"}


def test_export_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        export_vars({}, fmt="xml")


def test_import_dotenv_basic():
    text = 'FOO="bar"\nBAZ="qux"\n'
    result = import_vars(text, fmt="dotenv")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_import_dotenv_ignores_comments():
    text = '# comment\nFOO="bar"\n'
    result = import_vars(text, fmt="dotenv")
    assert "FOO" in result
    assert len(result) == 1


def test_import_dotenv_unquoted_value():
    result = import_vars("KEY=value", fmt="dotenv")
    assert result["KEY"] == "value"


def test_import_json_basic():
    import json
    text = json.dumps({"X": "y"})
    result = import_vars(text, fmt="json")
    assert result == {"X": "y"}


def test_import_json_non_object_raises():
    with pytest.raises(ValueError):
        import_vars("[1,2,3]", fmt="json")


def test_roundtrip_dotenv():
    original = {"A": "hello", "B": 'quo"ted'}
    assert import_vars(export_vars(original, "dotenv"), "dotenv") == original


def test_roundtrip_json():
    original = {"A": "hello", "B": "world"}
    assert import_vars(export_vars(original, "json"), "json") == original
