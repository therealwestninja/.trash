from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "test-results"
RESULTS_DIR.mkdir(exist_ok=True)

PYTHON = sys.executable
PLUGIN_PREFIX = "sweetie-plugin-"


def discover_plugins() -> list[str]:
    plugins_dir = ROOT / "plugins"
    return sorted(
        p.name for p in plugins_dir.iterdir() if p.is_dir() and p.name.startswith(PLUGIN_PREFIX)
    )


def selected_plugins() -> list[str]:
    raw = os.environ.get("SWEETIE_PLUGIN_FILTER", "").strip()
    if raw:
        return [part.strip() for part in raw.split(",") if part.strip()]
    return discover_plugins()


def run_pytest(label: str, args: list[str], *, timeout: int | None = None, extra_env: dict[str, str] | None = None) -> dict:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    started = time.time()
    cmd = [PYTHON, "-m", "pytest", *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        timed_out = False
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTimed out after {timeout} seconds.\n"
    duration = round(time.time() - started, 3)
    log_path = RESULTS_DIR / f"{label}.log"
    log_path.write_text(
        f"$ {' '.join(cmd)}\n\nSTDOUT\n{stdout}\n\nSTDERR\n{stderr}",
        encoding="utf-8",
    )
    return {
        "label": label,
        "command": cmd,
        "returncode": returncode,
        "timed_out": timed_out,
        "duration_seconds": duration,
        "log_file": str(log_path.relative_to(ROOT)),
    }


def summarize_status(runs: list[dict]) -> dict[str, int]:
    counter = Counter()
    for run in runs:
        if run["timed_out"]:
            counter["timed_out"] += 1
        elif run["returncode"] == 0:
            counter["passed"] += 1
        else:
            counter["failed"] += 1
    return dict(counter)


def write_reports(report: dict) -> None:
    json_path = RESULTS_DIR / "plugin-test-report.json"
    md_path = RESULTS_DIR / "plugin-test-report.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Plugin Test Report")
    lines.append("")
    lines.append(f"Generated: {report['generated_at_utc']}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Core run status: `{report['core_run']['returncode']}`")
    lines.append(f"- Fuzz plugin runs: {len(report['fuzz_runs'])}")
    lines.append(f"- Fuzz status summary: `{report['fuzz_status_summary']}`")
    lines.append(f"- Selected plugins: {', '.join(report['selected_plugins'])}")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- Core log: `{report['core_run']['log_file']}`")
    lines.append("- JSON summary: `test-results/plugin-test-report.json`")
    lines.append("- This Markdown summary: `test-results/plugin-test-report.md`")
    lines.append("")
    lines.append("## Fuzz runs")
    lines.append("")
    lines.append("| Plugin | Status | Return code | Time (s) | Log |")
    lines.append("|---|---:|---:|---:|---|")
    for run in report["fuzz_runs"]:
        status = "timed_out" if run["timed_out"] else ("passed" if run["returncode"] == 0 else "failed")
        lines.append(f"| {run['plugin']} | {status} | {run['returncode']} | {run['duration_seconds']} | `{run['log_file']}` |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    plugins = selected_plugins()
    fuzz_timeout = int(os.environ.get("SWEETIE_FUZZ_TIMEOUT_SECONDS", "45"))

    core_run = run_pytest(
        "core-suite",
        ["-q", "-m", "not slow"],
    )

    fuzz_runs = []
    for plugin in plugins:
        run = run_pytest(
            f"fuzz-{plugin}",
            ["-q", "tests/test_security_fuzz.py", "-k", "generic_fuzzed_json_never_500"],
            timeout=fuzz_timeout,
            extra_env={"SWEETIE_PLUGIN_FILTER": plugin},
        )
        run["plugin"] = plugin
        fuzz_runs.append(run)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_plugins": plugins,
        "core_run": core_run,
        "fuzz_runs": fuzz_runs,
        "fuzz_status_summary": summarize_status(fuzz_runs),
        "settings": {
            "fuzz_timeout_seconds": fuzz_timeout,
            "fuzz_examples": os.environ.get("SWEETIE_FUZZ_EXAMPLES", "8"),
            "max_probe_length": os.environ.get("SWEETIE_MAX_PROBE_LENGTH", "4096"),
            "fuzz_max_keys": os.environ.get("SWEETIE_FUZZ_MAX_KEYS", "6"),
            "fuzz_max_text": os.environ.get("SWEETIE_FUZZ_MAX_TEXT", "32"),
        },
    }
    write_reports(report)

    failed = core_run["returncode"] != 0 or any(r["returncode"] != 0 for r in fuzz_runs if not r["timed_out"]) or any(r["timed_out"] for r in fuzz_runs)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
