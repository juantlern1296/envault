"""Tag support for grouping environment variables."""
from envault.vault import load_vault, save_vault

TAGS_KEY = "__tags__"


def _get_tags(vault: dict) -> dict:
    return vault.get(TAGS_KEY, {})


def tag_var(vault_path: str, password: str, var: str, tag: str) -> None:
    """Associate a tag with a variable."""
    vault = load_vault(vault_path, password)
    tags = _get_tags(vault)
    tags.setdefault(tag, []).append(var)
    # deduplicate
    tags[tag] = list(dict.fromkeys(tags[tag]))
    vault[TAGS_KEY] = tags
    save_vault(vault_path, password, vault)


def untag_var(vault_path: str, password: str, var: str, tag: str) -> None:
    """Remove a tag from a variable."""
    vault = load_vault(vault_path, password)
    tags = _get_tags(vault)
    if tag not in tags or var not in tags[tag]:
        raise KeyError(f"{var!r} does not have tag {tag!r}")
    tags[tag].remove(var)
    if not tags[tag]:
        del tags[tag]
    vault[TAGS_KEY] = tags
    save_vault(vault_path, password, vault)


def list_tags(vault_path: str, password: str) -> dict:
    """Return mapping of tag -> list of vars."""
    vault = load_vault(vault_path, password)
    return dict(_get_tags(vault))


def vars_for_tag(vault_path: str, password: str, tag: str) -> list:
    """Return all variables with the given tag."""
    tags = list_tags(vault_path, password)
    return tags.get(tag, [])
