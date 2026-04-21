"""CLI commands for cloning variables between vaults."""
import click

from envault.clone import CloneError, clone_all, clone_var


@click.group(name="clone")
def clone_group():
    """Copy variables between vaults."""


@clone_group.command(name="var")
@click.argument("key")
@click.option("--src", required=True, envvar="ENVAULT_VAULT", help="Source vault file")
@click.option("--src-pass", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--dst", required=True, help="Destination vault file")
@click.option("--dst-pass", required=True, prompt=True, hide_input=True)
@click.option("--dest-key", default=None, help="Key name in destination (defaults to same key)")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite if key exists")
def cmd_clone_var(key, src, src_pass, dst, dst_pass, dest_key, overwrite):
    """Copy a single KEY from SRC vault to DST vault."""
    try:
        out_key = clone_var(src, src_pass, dst, dst_pass, key, dest_key, overwrite)
        click.echo(f"Cloned '{key}' -> '{out_key}'")
    except CloneError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@clone_group.command(name="all")
@click.option("--src", required=True, envvar="ENVAULT_VAULT", help="Source vault file")
@click.option("--src-pass", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--dst", required=True, help="Destination vault file")
@click.option("--dst-pass", required=True, prompt=True, hide_input=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
def cmd_clone_all(src, src_pass, dst, dst_pass, overwrite):
    """Copy ALL variables from SRC vault to DST vault."""
    results = clone_all(src, src_pass, dst, dst_pass, overwrite)
    ok = sum(1 for v in results.values() if v == "ok")
    skipped = sum(1 for v in results.values() if v == "skipped")
    for key, status in sorted(results.items()):
        icon = "✓" if status == "ok" else "–"
        click.echo(f"  {icon} {key} ({status})")
    click.echo(f"\nDone: {ok} copied, {skipped} skipped.")
