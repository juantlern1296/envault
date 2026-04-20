"""Export/import vault contents to/from common formats."""
import json
import os
from typing import Optional

SUPPORTED_FORMATS = ("dotenv", "json")


def export_vars(vars_dict: dict, fmt: str = "dotenv") -> str:
    """Serialize vars to the given format string."""
    if fmt == "dotenv":
        lines = []
        for k, v in vars_dict.items():
            escaped = v.replace('"', '\\"')
            lines.append(f'{k}="{escaped}"')
        return "\n".join(lines) + ("\n" if lines else "")
    elif fmt == "json":
        return json.dumps(vars_dict, indent=2) + "\n"
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Choose from {SUPPORTED_FORMATS}")


def import_vars(text: str, fmt: str = "dotenv") -> dict:
    """Parse vars from the given format string."""
    if fmt == "dotenv":
        result = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1].replace('\\"', '"')
            result[key] = value
        return result
    elif fmt == "json":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("JSON must be an object at the top level")
        return {str(k): str(v) for k, v in data.items()}
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Choose from {SUPPORTED_FORMATS}")
