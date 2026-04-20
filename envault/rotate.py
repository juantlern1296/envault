"""Key rotation: re-encrypt vault with a new password."""

from pathlib import Path
from envault.vault import load_vault, save_vault
from envault.audit import log_event


def rotate_key(vault_path: str, old_password: str, new_password: str) -> int:
    """Re-encrypt all vars in the vault under a new password.

    Returns the number of entries rotated.
    """
    path = Path(vault_path)
    if not path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    # Load with old password
    data = load_vault(vault_path, old_password)
    count = len(data)

    # Save with new password (overwrites existing file)
    save_vault(vault_path, new_password, data)

    log_event("rotate", {"vault": vault_path, "entries_rotated": count})
    return count
