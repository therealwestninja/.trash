from pathlib import Path
import yaml

def load_manifest(manifest_path: str | None = None) -> dict:
    path = Path(manifest_path or Path(__file__).resolve().parents[1] / "plugin.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
