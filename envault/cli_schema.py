"""CLI commands for schema management."""
import click

from envault.cli import get_password
from envault.schema import (
    VALID_TYPES,
    SchemaViolation,
    delete_schema,
    get_schema,
    set_schema,
    validate_all,
)


@click.group("schema")
def schema_group():
    """Manage variable schemas and validation rules."""


@schema_group.command("set")
@click.argument("key")
@click.option("--type", "type_", default="string", show_default=True,
              type=click.Choice(sorted(VALID_TYPES)), help="Expected value type")
@click.option("--required", is_flag=True, default=False, help="Mark variable as required")
@click.option("--pattern", default=None, help="Regex pattern the value must match")
@click.option("--description", default="", help="Human-readable description")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_set(key, type_, required, pattern, description, vault):
    """Define or update the schema for KEY."""
    password = get_password()
    try:
        set_schema(vault, password, key, type=type_, required=required,
                   pattern=pattern, description=description)
        click.echo(f"Schema set for '{key}'")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schema_group.command("get")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_get(key, vault):
    """Show the schema for KEY."""
    password = get_password()
    entry = get_schema(vault, password, key)
    if entry is None:
        click.echo(f"No schema defined for '{key}'")
        raise SystemExit(1)
    click.echo(f"key:         {key}")
    click.echo(f"type:        {entry.type}")
    click.echo(f"required:    {entry.required}")
    click.echo(f"pattern:     {entry.pattern or '(none)'}")
    click.echo(f"description: {entry.description or '(none)'}")


@schema_group.command("delete")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_delete(key, vault):
    """Remove the schema for KEY."""
    password = get_password()
    try:
        delete_schema(vault, password, key)
        click.echo(f"Schema deleted for '{key}'")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schema_group.command("validate")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_validate(vault):
    """Validate all vault variables against their schemas."""
    password = get_password()
    errors = validate_all(vault, password)
    if not errors:
        click.echo("All variables pass schema validation.")
    else:
        for key, msg in errors:
            click.echo(f"  FAIL  {key}: {msg}")
        raise SystemExit(1)
