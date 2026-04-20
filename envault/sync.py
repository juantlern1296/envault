"""Sync vault file to/from a remote location (S3 or file path)."""

import os
import shutil
from pathlib import Path


def _get_backend(remote: str):
    if remote.startswith("s3://"):
        return S3Backend(remote)
    return FileBackend(remote)


class FileBackend:
    def __init__(self, path: str):
        self.path = Path(path)

    def upload(self, local: Path) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local, self.path)

    def download(self, local: Path) -> bool:
        if not self.path.exists():
            return False
        local.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.path, local)
        return True

    def exists(self) -> bool:
        return self.path.exists()


class S3Backend:
    def __init__(self, url: str):
        self.url = url

    def _boto(self):
        try:
            import boto3
            return boto3.client("s3")
        except ImportError:
            raise RuntimeError("boto3 is required for S3 sync: pip install boto3")

    def _parse(self):
        parts = self.url[5:].split("/", 1)
        bucket = parts[0]
        if not bucket:
            raise ValueError(f"Invalid S3 URL, missing bucket: {self.url!r}")
        key = parts[1] if len(parts) > 1 else "envault.vault"
        if not key:
            raise ValueError(f"Invalid S3 URL, missing key: {self.url!r}")
        return bucket, key

    def upload(self, local: Path) -> None:
        bucket, key = self._parse()
        self._boto().upload_file(str(local), bucket, key)

    def download(self, local: Path) -> bool:
        import botocore
        bucket, key = self._parse()
        local.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._boto().download_file(bucket, key, str(local))
            return True
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code in ("404", "NoSuchKey"):
                return False
            raise

    def exists(self) -> bool:
        import botocore
        bucket, key = self._parse()
        try:
            self._boto().head_object(Bucket=bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code in ("404", "403"):
                return False
            raise


def push(local: Path, remote: str) -> None:
    """Upload local vault to remote."""
    if not local.exists():
        raise FileNotFoundError(f"Local vault file not found: {local}")
    backend = _get_backend(remote)
    backend.upload(local)


def pull(local: Path, remote: str) -> bool:
    """Download remote vault to local. Returns True if remote existed."""
    backend = _get_backend(remote)
    return backend.download(local)
