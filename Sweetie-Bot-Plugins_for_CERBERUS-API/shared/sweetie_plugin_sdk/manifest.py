from __future__ import annotations

from pathlib import Path
import yaml


def load_manifest(path: str | None = None):
    manifest_path = Path(path) if path else Path("plugin.yaml")
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
