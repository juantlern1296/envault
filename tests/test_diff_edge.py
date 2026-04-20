"""Edge cases for diff module."""
from envault.diff import diff_vaults


def test_both_empty():
    assert diff_vaults({}, {}) == []


def test_multiple_changes():
    old = {"A": "1", "B": "2", "C": "3"}
    new = {"A": "1", "B": "changed", "D": "4"}
    result = diff_vaults(old, new)
    statuses = {e.key: e.status for e in result}
    assert statuses["B"] == "changed"
    assert statuses["C"] == "removed"
    assert statuses["D"] == "added"
    assert "A" not in statuses


def test_show_unchanged_includes_all():
    old = {"A": "1", "B": "2"}
    new = {"A": "1", "B": "3"}
    result = diff_vaults(old, new, show_unchanged=True)
    statuses = {e.key: e.status for e in result}
    assert statuses["A"] == "unchanged"
    assert statuses["B"] == "changed"


def test_entry_values_correct():
    old = {"KEY": "old_val"}
    new = {"KEY": "new_val"}
    result = diff_vaults(old, new)
    assert result[0].old_value == "old_val"
    assert result[0].new_value == "new_val"


def test_large_diff_sorted():
    import string
    keys = list(string.ascii_uppercase)
    old = {k: str(i) for i, k in enumerate(keys)}
    new = {k: str(i + 1) for i, k in enumerate(keys)}
    result = diff_vaults(old, new)
    result_keys = [e.key for e in result]
    assert result_keys == sorted(result_keys)
    assert all(e.status == "changed" for e in result)
