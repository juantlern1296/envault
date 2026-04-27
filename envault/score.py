"""Vault health scoring — gives a numeric quality score to a vault."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envault.vault import load_vault
from envault.lint import lint_vault, LintIssue
from envault.ttl import is_expired
from envault.schema import _get_schemas, validate_vault


@dataclass
class ScoreReport:
    total: int
    score: int
    grade: str
    deductions: List[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 100.0
        return round(self.score / self.total * 100, 1)


GRADE_THRESHOLDS = [
    (90, "A"),
    (75, "B"),
    (60, "C"),
    (40, "D"),
    (0,  "F"),
]


def _grade(pct: float) -> str:
    for threshold, letter in GRADE_THRESHOLDS:
        if pct >= threshold:
            return letter
    return "F"


def score_vault(vault_path: str, password: str) -> ScoreReport:
    """Compute a health score (0-100) for the vault at *vault_path*."""
    try:
        data = load_vault(vault_path, password)
    except Exception as exc:
        return ScoreReport(total=100, score=0, grade="F",
                           deductions=[f"Cannot open vault: {exc}"])

    total = 100
    score = 100
    deductions: List[str] = []

    # Lint issues: -5 per issue, capped at -40
    issues: List[LintIssue] = lint_vault(vault_path, password)
    lint_penalty = min(len(issues) * 5, 40)
    if lint_penalty:
        score -= lint_penalty
        deductions.append(f"{len(issues)} lint issue(s) (-{lint_penalty} pts)")

    # Expired TTL keys: -3 per key, capped at -20
    expired = [k for k in data if is_expired(vault_path, password, k)]
    ttl_penalty = min(len(expired) * 3, 20)
    if ttl_penalty:
        score -= ttl_penalty
        deductions.append(f"{len(expired)} expired key(s) (-{ttl_penalty} pts)")

    # Schema violations: -5 per violation, capped at -30
    try:
        violations = validate_vault(vault_path, password)
        schema_penalty = min(len(violations) * 5, 30)
        if schema_penalty:
            score -= schema_penalty
            deductions.append(f"{len(violations)} schema violation(s) (-{schema_penalty} pts)")
    except Exception:
        pass

    score = max(score, 0)
    pct = score / total * 100
    return ScoreReport(total=total, score=score, grade=_grade(pct),
                       deductions=deductions)
