"""Namespace support: group vars under a named prefix for isolation."""

from envault.vault import load_vault, save_vault

SEP = "::"


def _ns_key(namespace: str, key: str) -> str:
    return f"{namespace}{SEP}{key}"


def ns_set(vault_path: str, password: str, namespace: str, key: str, value: str) -> None:
    """Set a variable under a namespace."""
    data = load_vault(vault_path, password)
    data[_ns_key(namespace, key)] = value
    save_vault(vault_path, password, data)


def ns_get(vault_path: str, password: str, namespace: str, key: str) -> str:
    """Get a variable from a namespace. Raises KeyError if missing."""
    data = load_vault(vault_path, password)
    full_key = _ns_key(namespace, key)
    if full_key not in data:
        raise KeyError(f"{namespace}{SEP}{key}")
    return data[full_key]


def ns_delete(vault_path: str, password: str, namespace: str, key: str) -> None:
    """Delete a variable from a namespace. Raises KeyError if missing."""
    data = load_vault(vault_path, password)
    full_key = _ns_key(namespace, key)
    if full_key not in data:
        raise KeyError(full_key)
    del data[full_key]
    save_vault(vault_path, password, data)


def list_namespaces(vault_path: str, password: str) -> list[str]:
    """Return a sorted list of all distinct namespace names."""
    data = load_vault(vault_path, password)
    namespaces = set()
    for k in data:
        if SEP in k:
            ns, _ = k.split(SEP, 1)
            namespaces.add(ns)
    return sorted(namespaces)


def ns_list_vars(vault_path: str, password: str, namespace: str) -> dict[str, str]:
    """Return all key/value pairs within a namespace (keys stripped of prefix)."""
    data = load_vault(vault_path, password)
    prefix = f"{namespace}{SEP}"
    return {k[len(prefix):]: v for k, v in data.items() if k.startswith(prefix)}


def ns_clear(vault_path: str, password: str, namespace: str) -> int:
    """Delete all variables under a namespace. Returns count of deleted entries."""
    data = load_vault(vault_path, password)
    prefix = f"{namespace}{SEP}"
    keys_to_delete = [k for k in data if k.startswith(prefix)]
    for k in keys_to_delete:
        del data[k]
    if keys_to_delete:
        save_vault(vault_path, password, data)
    return len(keys_to_delete)
