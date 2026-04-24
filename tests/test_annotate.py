"""Tests for envault.annotate."""
import pytest

from envault.annotate import (
    AnnotationError,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)
from envault.vault import save_vault, set_var

PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    p = str(tmp_path / "vault.enc")
    save_vault(p, PASSWORD, {})
    set_var(p, PASSWORD, "DB_HOST", "localhost")
    set_var(p, PASSWORD, "API_KEY", "abc123")
    return p


def test_set_annotation_creates_entry(vault_file):
    set_annotation(vault_file, PASSWORD, "DB_HOST", "primary database host")
    assert get_annotation(vault_file, "DB_HOST") == "primary database host"


def test_get_annotation_missing_key_returns_none(vault_file):
    assert get_annotation(vault_file, "DB_HOST") is None


def test_set_annotation_missing_vault_key_raises(vault_file):
    with pytest.raises(AnnotationError, match="NOT_EXIST"):
        set_annotation(vault_file, PASSWORD, "NOT_EXIST", "some note")


def test_set_annotation_overwrites_existing(vault_file):
    set_annotation(vault_file, PASSWORD, "DB_HOST", "first note")
    set_annotation(vault_file, PASSWORD, "DB_HOST", "second note")
    assert get_annotation(vault_file, "DB_HOST") == "second note"


def test_remove_annotation_deletes_entry(vault_file):
    set_annotation(vault_file, PASSWORD, "DB_HOST", "a note")
    remove_annotation(vault_file, "DB_HOST")
    assert get_annotation(vault_file, "DB_HOST") is None


def test_remove_annotation_missing_raises(vault_file):
    with pytest.raises(AnnotationError, match="No annotation"):
        remove_annotation(vault_file, "DB_HOST")


def test_list_annotations_returns_all(vault_file):
    set_annotation(vault_file, PASSWORD, "DB_HOST", "host note")
    set_annotation(vault_file, PASSWORD, "API_KEY", "key note")
    result = list_annotations(vault_file)
    assert result == {"DB_HOST": "host note", "API_KEY": "key note"}


def test_list_annotations_empty_vault(vault_file):
    assert list_annotations(vault_file) == {}


def test_annotations_stored_separately_from_vault(vault_file, tmp_path):
    """Annotation file must not be the vault file itself."""
    import json
    from pathlib import Path

    set_annotation(vault_file, PASSWORD, "DB_HOST", "note")
    ann_path = Path(vault_file).with_suffix(".annotations.json")
    data = json.loads(ann_path.read_text())
    assert "DB_HOST" in data
