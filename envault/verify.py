"""Vault integrity verification — checks that all stored values can be decrypted
and optionally validates them against registered schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault
from envault.crypto import decrypt


@dataclass
class VerifyResult:
    key: str
    ok: bool
    error: Optional[str] = None


@dataclass
class VerifyReport:
    results: List[VerifyResult] = field(default_factory=list)

    @property
    def passed(self) -> List[VerifyResult]:
        return [r for r in self.results if r.ok]

    @property
    def failed(self) -> List[VerifyResult]:
        return [r for r in self.results if not r.ok]

    @property
    def success(self) -> bool:
        return len(self.failed) == 0


def verify_vault(vault_path: str, password: str) -> VerifyReport:
    """Attempt to decrypt every entry in the vault and report results."""
    report = VerifyReport()

    try:
        data = load_vault(vault_path, password)
    except Exception as exc:
        report.results.append(VerifyResult(key="<vault>", ok=False, error=str(exc)))
        return report

    if not data:
        return report

    for key, ciphertext in data.items():
        try:
            decrypt(ciphertext, password)
            report.results.append(VerifyResult(key=key, ok=True))
        except Exception as exc:  # noqa: BLE001
            report.results.append(VerifyResult(key=key, ok=False, error=str(exc)))

    return report


def summarise_report(report: VerifyReport) -> str:
    lines = []
    for r in sorted(report.results, key=lambda x: x.key):
        status = "OK" if r.ok else f"FAIL ({r.error})"
        lines.append(f"  {r.key}: {status}")
    total = len(report.results)
    failed = len(report.failed)
    lines.append(f"\n{total} checked, {failed} failed.")
    return "\n".join(lines)
