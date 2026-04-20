"""CLI commands for variable history."""
import os
import click
from datetime import datetime
from envault.history import get_history, clear_history


@click.group("history")
def history_group():
    """View and manage variable change history."""


@history_group.command("show")
@click.argument("key")
def cmd_show(key):
    """Show change history for KEY."""
    vault_path = os.environ.get("ENVAULT_PATH", "vault.enc")
    entries = get_history(vault_path, key)
    if not entries:
        click.echo(f"No history for '{key}'.")
        return
    click.echo(f"History for '{key}':")
    for e in entries:
        ts = datetime.fromtimestamp(e["ts"]).strftime("%Y-%m-%d %H:%M:%S")
        action = e["action"]
        line = f"  [{ts}] {action}"
        if "old_value" in e:
            line += f"  (old: {e['old_value']})"
        click.echo(line)


@history_group.command("clear")
@click.argument("key", required=False, default=None)
@click.option("--all", "all_keys", is_flag=True, help="Clear history for all keys.")
def cmd_clear(key, all_keys):
    """Clear history for KEY or all keys."""
    vault_path = os.environ.get("ENVAULT_PATH", "vault.enc")
    if all_keys:
        clear_history(vault_path)
        click.echo("Cleared all history.")
    elif key:
        clear_history(vault_path, key)
        click.echo(f"Cleared history for '{key}'.")
    else:
        click.echo("Specify a KEY or use --all.", err=True)
        raise SystemExit(1)
