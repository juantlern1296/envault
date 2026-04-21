"""Quota management: limit the number of variables stored in a vault or namespace."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault

_QUOTA_KEY = "__quotas__"


class QuotaExceeded(Exception):
    """Raised when adding a variable would exceed the configured quota."""


def _get_quotas(vault_file: Path, password: str) -> dict:
    data = load_vault(vault_file, password)
    return data.get(_QUOTA_KEY, {})


def _save_quotas(vault_file: Path, password: str, quotas: dict) -> None:
    data = load_vault(vault_file, password)
    data[_QUOTA_KEY] = quotas
    save_vault(vault_file, password, data)


def set_quota(vault_file: Path, password: str, namespace: str, limit: int) -> None:
    """Set the maximum number of variables allowed in *namespace*."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    quotas = _get_quotas(vault_file, password)
    quotas[namespace] = limit
    _save_quotas(vault_file, password, quotas)


def get_quota(vault_file: Path, password: str, namespace: str) -> Optional[int]:
    """Return the quota for *namespace*, or None if no quota is set."""
    return _get_quotas(vault_file, password).get(namespace)


def delete_quota(vault_file: Path, password: str, namespace: str) -> None:
    """Remove the quota for *namespace*."""
    quotas = _get_quotas(vault_file, password)
    if namespace not in quotas:
        raise KeyError(f"No quota set for namespace '{namespace}'.")
    del quotas[namespace]
    _save_quotas(vault_file, password, quotas)


def check_quota(vault_file: Path, password: str, namespace: str) -> None:
    """Raise QuotaExceeded if the namespace has reached its limit.

    Counts keys that belong to *namespace* (prefix ``<namespace>::``) or,
    for the special namespace ``"global"``, all non-internal keys.
    """
    limit = get_quota(vault_file, password, namespace)
    if limit is None:
        return  # no quota configured

    data = load_vault(vault_file, password)
    internal = {_QUOTA_KEY, "__tags__", "__ttl__", "__pins__", "__aliases__",
                "__schemas__", "__acl__", "__snapshots__", "__webhooks__",
                "__reminders__", "__quotas__"}

    if namespace == "global":
        count = sum(1 for k in data if k not in internal and "::" not in k)
    else:
        prefix = f"{namespace}::"
        count = sum(1 for k in data if k.startswith(prefix))

    if count >= limit:
        raise QuotaExceeded(
            f"Quota of {limit} variable(s) exceeded for namespace '{namespace}'."
        )
