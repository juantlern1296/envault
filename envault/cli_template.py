"""CLI commands for template rendering."""

import click

from envault.cli import get_password
from envault.template import render_string, render_file


@click.group(name="template")
def template_group():
    """Render templates using vault variables."""


@template_group.command(name="render")
@click.argument("src", type=click.Path(exists=True))
@click.argument("dst", type=click.Path())
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
@click.option("--no-strict", is_flag=True, default=False, help="Leave unknown placeholders intact.")
def cmd_render(src: str, dst: str, vault: str, no_strict: bool):
    """Render template file SRC into DST, substituting vault variables."""
    password = get_password()
    try:
        keys = render_file(src, dst, vault, password, strict=not no_strict)
        click.echo(f"Rendered {dst} ({len(keys)} variable(s) substituted: {', '.join(keys) or 'none'})")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@template_group.command(name="echo")
@click.argument("template_str")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
def cmd_echo(template_str: str, vault: str):
    """Render a template string and print the result."""
    password = get_password()
    try:
        result = render_string(template_str, vault, password)
        click.echo(result)
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
