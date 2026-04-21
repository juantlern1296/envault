"""CLI subcommand for viewing the envault audit log."""

import click
from pathlib import Path
from envault.audit import read_log, clear_log, DEFAULT_LOG_PATH


@click.group()
def audit():
    """View and manage the audit log."""
    pass


@audit.command("list")
@click.option("--log", default=None, help="Path to audit log file.")
@click.option("--action", default=None, help="Filter by action (set/get/delete).")
@click.option("--limit", default=50, show_default=True, help="Max entries to show.")
def cmd_list(log, action, limit):
    """Print recent audit log entries."""
    log_path = Path(log) if log else DEFAULT_LOG_PATH
    try:
        entries = read_log(log_path)
    except OSError as e:
        raise click.ClickException(f"Could not read audit log: {e}")
    if action:
        entries = [e for e in entries if e.get("action") == action]
    entries = entries[-limit:]
    if not entries:
        click.echo("No audit log entries found.")
        return
    for e in entries:
        status = "OK" if e.get("success") else "FAIL"
        key_part = f" key={e['key']}" if e.get("key") else ""
        click.echo(f"[{e['timestamp']}] {e['action'].upper()}{key_part} ({status})")


@audit.command("clear")
@click.option("--log", default=None, help="Path to audit log file.")
@click.confirmation_option(prompt="Clear the entire audit log?")
def cmd_clear(log):
    """Delete all audit log entries."""
    log_path = Path(log) if log else DEFAULT_LOG_PATH
    try:
        clear_log(log_path)
    except OSError as e:
        raise click.ClickException(f"Could not clear audit log: {e}")
    click.echo("Audit log cleared.")
