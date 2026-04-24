"""CLI commands for managing key annotations."""
import click

from envault.annotate import (
    AnnotationError,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)
from envault.cli import get_password


@click.group("annotate")
def annotate_group():
    """Attach notes/metadata to vault keys."""


@annotate_group.command("set")
@click.argument("key")
@click.argument("note")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_set(key: str, note: str, vault: str):
    """Set an annotation NOTE on KEY."""
    password = get_password()
    try:
        set_annotation(vault, password, key, note)
        click.echo(f"Annotation set for '{key}'.")
    except AnnotationError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@annotate_group.command("get")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_get(key: str, vault: str):
    """Print the annotation for KEY."""
    note = get_annotation(vault, key)
    if note is None:
        click.echo(f"No annotation for '{key}'.", err=True)
        raise SystemExit(1)
    click.echo(note)


@annotate_group.command("remove")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_remove(key: str, vault: str):
    """Remove the annotation for KEY."""
    try:
        remove_annotation(vault, key)
        click.echo(f"Annotation removed for '{key}'.")
    except AnnotationError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@annotate_group.command("list")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_list(vault: str):
    """List all annotations."""
    annotations = list_annotations(vault)
    if not annotations:
        click.echo("No annotations.")
        return
    for key, note in sorted(annotations.items()):
        click.echo(f"{key}: {note}")
