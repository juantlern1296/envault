"""Profile support — named sets of env vars (e.g. dev, prod)."""
from __future__ import annotations

from typing import Dict

from envault.vault import load_vault, save_vault

PROFILE_PREFIX = "__profile__"


def _profile_key(profile: str, var: str) -> str:
    return f"{PROFILE_PREFIX}{profile}__{var}"


def set_profile_var(vault_path: str, password: str, profile: str, key: str, value: str) -> None:
    data = load_vault(vault_path, password)
    data[_profile_key(profile, key)] = value
    save_vault(vault_path, password, data)


def get_profile_var(vault_path: str, password: str, profile: str, key: str) -> str:
    data = load_vault(vault_path, password)
    full_key = _profile_key(profile, key)
    if full_key not in data:
        raise KeyError(f"Key '{key}' not found in profile '{profile}'")
    return data[full_key]


def delete_profile_var(vault_path: str, password: str, profile: str, key: str) -> None:
    data = load_vault(vault_path, password)
    full_key = _profile_key(profile, key)
    if full_key not in data:
        raise KeyError(f"Key '{key}' not found in profile '{profile}'")
    del data[full_key]
    save_vault(vault_path, password, data)


def list_profiles(vault_path: str, password: str) -> Dict[str, list]:
    data = load_vault(vault_path, password)
    profiles: Dict[str, list] = {}
    for k in data:
        if k.startswith(PROFILE_PREFIX):
            rest = k[len(PROFILE_PREFIX):]
            profile, _, var = rest.partition("__")
            profiles.setdefault(profile, []).append(var)
    return profiles


def list_profile_vars(vault_path: str, password: str, profile: str) -> Dict[str, str]:
    data = load_vault(vault_path, password)
    prefix = _profile_key(profile, "")
    return {
        k[len(prefix):]: v
        for k, v in data.items()
        if k.startswith(prefix)
    }
