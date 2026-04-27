"""CLI commands for vault health scoring."""
import click

from envault.cli import get_password
from envault.score import score_vault


@click.group("score")
def score_group() -> None:
    """Vault health scoring commands."""


@score_group.command("run")
@click.option("--vault", envvar="ENVAULT_PATH", required=True,
              help="Path to the vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None,
              help="Vault password (prompted if omitted).")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output results as JSON.")
def cmd_run(vault: str, password: str | None, as_json: bool) -> None:
    """Score the vault and print a health report."""
    pw = password or get_password()
    report = score_vault(vault, pw)

    if as_json:
        import json
        click.echo(json.dumps({
            "score": report.score,
            "total": report.total,
            "percentage": report.percentage,
            "grade": report.grade,
            "deductions": report.deductions,
        }))
        return

    click.echo(f"Vault Health Score: {report.score}/{report.total} "
               f"({report.percentage}%)  Grade: {report.grade}")
    if report.deductions:
        click.echo("Deductions:")
        for d in report.deductions:
            click.echo(f"  - {d}")
    else:
        click.echo("No issues found — vault looks great!")

    raise SystemExit(0 if report.grade in ("A", "B") else 1)
