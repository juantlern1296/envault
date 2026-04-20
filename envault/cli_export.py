"""CLI commands for exporting and importing vault contents."""
import sys
import click
from envault.vault import load_vault, set_var
from envault.export import export_vars, import_vars, SUPPORTED_FORMATS
from envault.cli import get_password
from envault.audit import log_event


@click.group()
def export_group():
    """Export and import vault variables."""


@export_group.command("export")
@click.option("--format", "fmt", default="dotenv", show_default=True,
              type=click.Choice(SUPPORTED_FORMATS), help="Output format.")
@click.option("--output", "-o", default="-", help="Output file (default: stdout).")
@click.pass_context
def cmd_export(ctx, fmt, output):
    """Export all variables from the vault."""
    vault_path = ctx.obj["vault"]
    password = get_password()
    try:
        data = load_vault(vault_path, password)
    except Exception as e:
        click.echo(f"Error loading vault: {e}", err=True)
        sys.exit(1)

    text = export_vars(data, fmt=fmt)
    if output == "-":
        click.echo(text, nl=False)
    else:
        with open(output, "w") as f:
            f.write(text)
        click.echo(f"Exported {len(data)} variable(s) to {output}")
    log_event("export", {"format": fmt, "count": len(data)})


@export_group.command("import")
@click.argument("input_file")
@click.option("--format", "fmt", default="dotenv", show_default=True,
              type=click.Choice(SUPPORTED_FORMATS), help="Input format.")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys without prompting.")
@click.pass_context
def cmd_import(ctx, input_file, fmt, overwrite):
    """Import variables into the vault from a file."""
    vault_path = ctx.obj["vault"]
    password = get_password()

    try:
        with open(input_file) as f:
            text = f.read()
        incoming = import_vars(text, fmt=fmt)
    except Exception as e:
        click.echo(f"Error reading import file: {e}", err=True)
        sys.exit(1)

    try:
        existing = load_vault(vault_path, password)
    except Exception:
        existing = {}

    skipped = 0
    imported = 0
    for key, value in incoming.items():
        if key in existing and not overwrite:
            click.echo(f"Skipping existing key: {key}")
            skipped += 1
            continue
        set_var(vault_path, password, key, value)
        imported += 1

    log_event("import", {"format": fmt, "imported": imported, "skipped": skipped})
    click.echo(f"Imported {imported} variable(s), skipped {skipped}.")
