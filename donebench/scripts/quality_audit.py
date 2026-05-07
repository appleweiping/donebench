from __future__ import annotations

import json
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.core.validation import validate_tasks


def _raw_tasks(root: Path) -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(root.rglob("*.json"))]


def lexical_duplicate_pairs(tasks: list[dict[str, Any]], threshold: float = 0.92) -> list[dict[str, Any]]:
    pairs = []
    for i, left in enumerate(tasks):
        for right in tasks[i + 1 :]:
            if left["domain"] != right["domain"]:
                continue
            ratio = SequenceMatcher(None, left["user_goal"], right["user_goal"]).ratio()
            if ratio >= threshold:
                pairs.append({"left": left["task_id"], "right": right["task_id"], "domain": left["domain"], "similarity": ratio})
    return pairs


def criterion_signature(task: dict[str, Any]) -> str:
    atoms = task.get("criterion_atoms", [])
    keys = [
        (
            atom.get("kind"),
            atom.get("modality"),
            atom.get("operator"),
            atom.get("evidence_source"),
        )
        for atom in atoms
    ]
    return json.dumps(keys, sort_keys=True)


def donespec_signature(node: Any) -> Any:
    if isinstance(node, dict):
        if "all" in node:
            return {"all": [donespec_signature(item) for item in node["all"]]}
        if "any" in node:
            return {"any": [donespec_signature(item) for item in node["any"]]}
        if "not" in node:
            return {"not": donespec_signature(node["not"])}
        return sorted(node.keys())
    if isinstance(node, list):
        return [donespec_signature(item) for item in node]
    return type(node).__name__


def structural_leakage(raw: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    by_signature: dict[str, list[str]] = defaultdict(list)
    for task in raw:
        signature = criterion_signature(task)
        by_signature[signature].append(task["task_id"])
        metadata = task.get("generation_metadata", {})
        audit = task.get("audit", {})
        rows.append(
            {
                "task_id": task["task_id"],
                "domain": task["domain"],
                "split": audit.get("split"),
                "difficulty": task.get("difficulty"),
                "task_pattern": task.get("task_pattern") or metadata.get("pattern_id") or audit.get("task_pattern"),
                "scenario_id": metadata.get("scenario_id") or audit.get("scenario_id"),
                "criterion_signature": signature,
                "donespec_signature": json.dumps(donespec_signature(task.get("gold_donespec", {})), sort_keys=True),
                "mutation_signature": "|".join(sorted(miss.get("mutation_taxon") or miss.get("mutation_id", "") for miss in task.get("near_miss_states", []))),
            }
        )
    leakage_rows = []
    for key in ["task_pattern", "scenario_id", "criterion_signature", "donespec_signature", "mutation_signature"]:
        for value, group in pd.DataFrame(rows).groupby(key):
            splits = sorted(set(group["split"]))
            leakage_rows.append(
                {
                    "field": key,
                    "value": str(value)[:240],
                    "num_tasks": len(group),
                    "splits": "|".join(splits),
                    "num_domains": group["domain"].nunique(),
                    "example_task_ids": "|".join(group["task_id"].head(8)),
                    "leaks_across_dev_test": "dev" in splits and "test" in splits,
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(leakage_rows)


def quality_audit(root: Path, output_dir: Path) -> dict[str, Any]:
    tasks, validation_errors = validate_tasks(root)
    raw = _raw_tasks(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for task, item in zip(tasks, raw):
        mutation_taxa = [miss.get("mutation_taxon") or miss.get("mutation_id") for miss in item.get("near_miss_states", [])]
        rows.append(
            {
                "task_id": task.task_id,
                "domain": task.domain,
                "difficulty": task.difficulty,
                "split": task.audit.split,
                "task_pattern": task.task_pattern or task.audit.task_pattern,
                "goal_chars": len(task.user_goal),
                "num_hard_atoms": len([a for a in task.criterion_atoms if a.criticality == "hard"]),
                "num_failure_atoms": len([a for a in task.criterion_atoms if a.kind == "failure"]),
                "num_required_observations": len([a for a in task.criterion_atoms if a.kind == "required_observation"]),
                "num_near_misses": len(task.near_miss_states),
                "mutation_taxa": "|".join(sorted(set(mutation_taxa))),
            }
        )
    df = pd.DataFrame(rows)
    duplicates = pd.DataFrame(lexical_duplicate_pairs(raw))
    structure, leakage = structural_leakage(raw)
    pattern_split = (
        structure.groupby(["task_pattern", "split"], as_index=False)
        .size()
        .sort_values(["task_pattern", "split"])
    )
    scenario_split = (
        structure.groupby(["scenario_id", "split"], as_index=False)
        .size()
        .sort_values(["scenario_id", "split"])
    )
    summary = {
        "num_tasks": len(tasks),
        "validation_errors": validation_errors,
        "by_domain": Counter(df["domain"]).copy(),
        "by_split": Counter(df["split"]).copy(),
        "by_difficulty": Counter(df["difficulty"]).copy(),
        "num_high_similarity_pairs": len(duplicates),
        "num_structural_signature_groups": int(structure["criterion_signature"].nunique()),
        "num_donespec_signature_groups": int(structure["donespec_signature"].nunique()),
        "num_pattern_dev_test_leaks": int(leakage[(leakage["field"] == "task_pattern") & (leakage["leaks_across_dev_test"])].shape[0]),
        "num_scenario_dev_test_leaks": int(leakage[(leakage["field"] == "scenario_id") & (leakage["leaks_across_dev_test"])].shape[0]),
    }
    df.to_csv(output_dir / "task_quality_audit.csv", index=False)
    duplicates.to_csv(output_dir / "task_near_duplicates.csv", index=False)
    structure.to_csv(output_dir / "task_structural_signatures.csv", index=False)
    leakage.to_csv(output_dir / "task_family_leakage.csv", index=False)
    pattern_split.to_csv(output_dir / "task_pattern_split.csv", index=False)
    scenario_split.to_csv(output_dir / "task_scenario_split.csv", index=False)
    write_datasheet(summary, output_dir / "task_construction_datasheet.md")
    (output_dir / "task_quality_summary.json").write_text(json.dumps(summary, indent=2, default=dict), encoding="utf-8")
    return summary


def write_datasheet(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# DoneBench Task Construction Datasheet",
        "",
        "## Purpose",
        "",
        "DoneBench tasks isolate completion-semantics grounding: the model must infer what counts as done before acting.",
        "",
        "## Construction",
        "",
        "- Tasks are generated across five workflow-style domains with balanced dev/test splits.",
        "- Each task contains gold criterion atoms, an executable DoneSpec, a reference trace, and five near-miss final states.",
        "- Near misses cover participant/recipient omission, missing policy confirmation, conflict injection, incomplete terminal state, and unrelated side effect.",
        "",
        "## Audit Signals",
        "",
        f"- Number of tasks: {summary['num_tasks']}",
        f"- High lexical duplicate pairs: {summary['num_high_similarity_pairs']}",
        f"- Criterion structural signature groups: {summary['num_structural_signature_groups']}",
        f"- DoneSpec structural signature groups: {summary['num_donespec_signature_groups']}",
        f"- Task-pattern dev/test overlaps: {summary['num_pattern_dev_test_leaks']}",
        f"- Scenario dev/test overlaps: {summary['num_scenario_dev_test_leaks']}",
        "",
        "## Known Risks",
        "",
        "The current topconf-2 set is generated from a controlled grammar. Reports therefore include lexical duplicate, structural signature, pattern split, scenario split, and family leakage tables. Paper claims should treat this as a controlled semantic benchmark unless a human-authored heterogeneity subset is added.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
