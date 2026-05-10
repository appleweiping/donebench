from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any


INCLUDED_ARTIFACTS = [
    "README.md",
    "Dockerfile",
    ".devcontainer/devcontainer.json",
    "Makefile",
    "pyproject.toml",
    "configs/experiments.yaml",
    "configs/models.yaml",
    "data/tasks",
    "donebench",
    "tests",
    "paper/main.tex",
    "paper/sections",
    "paper/tables",
    "reports/artifact_policy.md",
    "reports/claim_to_artifact_map.md",
    "reports/leaderboard_contamination_policy.md",
    "reports/model_access_cost_latency_retry.md",
    "reports/full_run_readiness.json",
    "reports/full_runs/runs/topconf_deepseek_toolplan_full",
    "reports/ablations/runs/topconf_oracle_spec_reference",
    "reports/ablations/runs/topconf_deepseek_token_matched",
    "reports/ablations/runs/topconf_deepseek_repaired_diagnostic_slice",
    "reports/strict_validation",
    "reports/audit_repaired_human_queue_structured",
    "reports/calibration_packets",
]

RAW_TRACES = [
    "results/runs/topconf_deepseek_toolplan_full/trials.jsonl",
    "results/runs/topconf_deepseek_token_matched/trials.jsonl",
    "results/runs/topconf_oracle_spec_reference/trials.jsonl",
    "results/runs/topconf_deepseek_repaired_diagnostic_slice/trials.jsonl",
]

HISTORICAL_OR_EXCLUDED = [
    "reports/audit_full_domain_model_assisted",
    "reports/audit_deepseek_gpt55_merged",
    "reports/audit_gpt52_full_domain",
    "results/topconf_deepseek_core_trial0.jsonl",
]


def write_release_manifest(output_dir: Path = Path("reports")) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "release_id": f"donebench-{date.today().isoformat()}",
        "release_date": date.today().isoformat(),
        "git_commit_at_generation": _git_commit(),
        "dataset_version": "topconf-4.1-repaired-2026-05-10",
        "current_readiness_path": "reports/full_run_readiness.json",
        "paper_table_policy_path": "reports/artifact_policy.md",
        "raw_trace_policy": "Existing tracked raw traces are included when already tracked. Future hosted-model raw trials under results/runs/*/trials.jsonl should be published via Git LFS or release artifacts, with manifests and aggregate tables committed.",
        "included_artifacts": [_artifact_entry(Path(path)) for path in INCLUDED_ARTIFACTS],
        "raw_traces": [_artifact_entry(Path(path)) for path in RAW_TRACES],
        "excluded_or_historical_artifacts": [_artifact_entry(Path(path)) for path in HISTORICAL_OR_EXCLUDED],
        "large_artifact_locations": [
            {
                "path": "results/runs/*/trials.jsonl",
                "policy": "Use Git LFS or external release artifact for new large hosted-model traces.",
            }
        ],
        "reproduction_commands": {
            "offline_smoke": "make repro-smoke",
            "validate": "python -m donebench.cli validate data\\tasks",
            "strict_validation": "python -m donebench.cli strict-validation data\\tasks reports\\strict_validation",
            "main_postprocess": "python -m donebench.cli experiment-pipeline topconf_deepseek_toolplan_full --output results\\runs\\topconf_deepseek_toolplan_full\\trials.jsonl --report-root reports\\full_runs --postprocess-only",
            "refresh_paper_tables": "python -m donebench.cli refresh-paper-tables",
            "repaired_confirmation_slice": "python -m donebench.cli experiment-pipeline topconf_deepseek_repaired_diagnostic_slice --output results\\runs\\topconf_deepseek_repaired_diagnostic_slice\\trials.jsonl --report-root reports\\ablations --limit 100 --max-workers 0 --resume",
        },
        "known_blockers": [
            "LaTeX PDF compile and visual inspection require a TeX-enabled environment.",
            "Cross-family slices remain pending provider credentials/results and must not support cross-family claims yet.",
            "Optional true human calibration remains incomplete until real annotators fill the human annotation fields.",
        ],
        "claims_not_supported": [
            "DoneBench is more realistic than WebArena, OSWorld, WorkArena, or tau-bench.",
            "spec_first robustly improves task execution success.",
            "The diagnostic taxonomy is human-validated.",
            "Current results generalize across model families.",
        ],
    }
    json_path = output_dir / "release_manifest.json"
    md_path = output_dir / "release_manifest.md"
    json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _write_markdown(md_path, manifest)
    return manifest


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _artifact_entry(path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "path": str(path),
        "present": path.exists(),
        "kind": "directory" if path.is_dir() else "file",
    }
    if path.exists() and path.is_file():
        entry["bytes"] = path.stat().st_size
        entry["sha256"] = _sha256(path)
    elif path.exists() and path.is_dir():
        files = sorted(child for child in path.rglob("*") if child.is_file() and not _is_cache_artifact(child))
        entry["files"] = len(files)
        entry["sample_files"] = [str(child) for child in files[:10]]
    return entry


def _is_cache_artifact(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_markdown(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# Release Manifest",
        "",
        f"- Release id: `{manifest['release_id']}`",
        f"- Git commit at generation: `{manifest['git_commit_at_generation']}`",
        f"- Dataset version: `{manifest['dataset_version']}`",
        f"- Readiness: `{manifest['current_readiness_path']}`",
        f"- Paper table policy: `{manifest['paper_table_policy_path']}`",
        "",
        "## Raw Trace Policy",
        "",
        manifest["raw_trace_policy"],
        "",
        "## Included Artifact Groups",
        "",
    ]
    for item in manifest["included_artifacts"]:
        status = "present" if item["present"] else "missing"
        lines.append(f"- [{status}] `{item['path']}`")
    lines.extend(["", "## Known Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in manifest["known_blockers"])
    lines.extend(["", "## Claims Not Supported", ""])
    lines.extend(f"- {claim}" for claim in manifest["claims_not_supported"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
