from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO_ROOT / "plugins"


def parse_routes(main_py: Path) -> list[dict[str, Any]]:
    if not main_py.exists():
        return []
    route_file = main_py.parent / "routes.py"
    target = route_file if route_file.exists() else main_py
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    routes: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.upper()
            if method not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
                continue
            if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                continue
            routes.append({"method": method, "path": decorator.args[0].value, "handler": node.name})
    return sorted(routes, key=lambda r: (r["path"], r["method"]))


def parse_execute_actions(source_file: Path) -> list[str]:
    if not source_file.exists():
        return []
    candidates = [source_file, source_file.parent / "routes.py"]
    actions: set[str] = set()
    for candidate in candidates:
        if not candidate.exists():
            continue
        tree = ast.parse(candidate.read_text(encoding="utf-8"), filename=str(candidate))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare) or len(node.ops) != 1:
                continue
            comparator = node.comparators[0]
            if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                value = comparator.value
                if "." in value:
                    actions.add(value)
    return sorted(actions)


def build_report() -> dict[str, Any]:
    report: dict[str, Any] = {"plugins": []}
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        manifest_path = plugin_dir / "plugin.yaml"
        if not manifest_path.exists():
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        main_py = plugin_dir / "app" / "main.py"
        report["plugins"].append(
            {
                "name": manifest.get("name", plugin_dir.name),
                "path": str(plugin_dir.relative_to(REPO_ROOT)),
                "manifest": manifest,
                "routes": parse_routes(main_py),
                "execute_actions_seen_in_code": parse_execute_actions(main_py),
            }
        )
    return report


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))
