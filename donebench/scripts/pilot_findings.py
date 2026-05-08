from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class PilotRun:
    key: str
    label: str
    report_dir: Path
    notes: str


DEFAULT_RUNS = [
    PilotRun(
        key="standard_toolplan",
        label="Standard tool-plan pilot",
        report_dir=Path("reports/stratified_runs/runs/topconf_deepseek_toolplan_pilot"),
        notes="50 stratified tasks, 3 protocols, 2 DeepSeek-family models, 1 trial per task.",
    ),
    PilotRun(
        key="token_matched",
        label="Token-matched pilot",
        report_dir=Path("reports/token_matched_runs/runs/topconf_deepseek_token_matched"),
        notes="50 stratified tasks, token-matched protocol prompts, 2 DeepSeek-family models, 1 trial per task.",
    ),
    PilotRun(
        key="replicates_5x",
        label="5-trial replicates pilot",
        report_dir=Path("reports/replicate_runs/runs/topconf_deepseek_toolplan_replicates_pilot"),
        notes="50 stratified tasks, 3 protocols, 2 DeepSeek-family models, 5 trials per task.",
    ),
]


def write_pilot_findings(
    output: Path = Path("reports/pilot_findings.md"),
    comparison_csv: Path = Path("paper/tables/pilot_comparison.csv"),
    runs: list[PilotRun] | None = None,
) -> dict[str, Any]:
    runs = runs or DEFAULT_RUNS
    output.parent.mkdir(parents=True, exist_ok=True)
    comparison_csv.parent.mkdir(parents=True, exist_ok=True)

    comparison = build_comparison_table(runs)
    domain = build_domain_table(runs)
    parse = build_parse_table(runs)
    cost = build_cost_table(runs)

    comparison.to_csv(comparison_csv, index=False)
    domain_csv = comparison_csv.with_name("pilot_domain_patterns.csv")
    parse_csv = comparison_csv.with_name("pilot_parse_caveats.csv")
    cost_csv = comparison_csv.with_name("pilot_costs.csv")
    domain.to_csv(domain_csv, index=False)
    parse.to_csv(parse_csv, index=False)
    cost.to_csv(cost_csv, index=False)

    output.write_text(
        render_markdown(
            runs=runs,
            comparison=comparison,
            domain=domain,
            parse=parse,
            cost=cost,
            comparison_csv=comparison_csv,
            domain_csv=domain_csv,
            parse_csv=parse_csv,
            cost_csv=cost_csv,
        ),
        encoding="utf-8",
    )
    return {
        "pilot_findings": str(output),
        "comparison_csv": str(comparison_csv),
        "domain_csv": str(domain_csv),
        "parse_csv": str(parse_csv),
        "cost_csv": str(cost_csv),
        "rows": len(comparison),
    }


def build_comparison_table(runs: list[PilotRun]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run in runs:
        summary = _read_csv(run.report_dir / "stats" / "advanced_summary_ci.csv")
        passk = _read_csv(run.report_dir / "stats" / "advanced_passk_consistency.csv")
        parse = _read_csv(run.report_dir / "parse" / "parse_transparency_by_model_agent.csv")
        for _, row in summary.iterrows():
            model = str(row["model"])
            agent = str(row["agent"])
            match = _match_row(passk, model, agent)
            parse_match = _match_row(parse, model, agent)
            max_k = int(match.get("max_k", 1)) if match else 1
            rows.append(
                {
                    "run_key": run.key,
                    "run": run.label,
                    "model": model,
                    "agent": agent,
                    "agent_family": agent.replace("_token_matched", ""),
                    "n_trials": int(row["n"]),
                    "n_tasks": int(match.get("n_tasks", row["n"])) if match else int(row["n"]),
                    "k": max_k,
                    "cc_f1_pct": _pct(row["cc_f1_mean"]),
                    "donespec_valid_pct": _pct(row["donespec_valid_mean"]),
                    "near_miss_detection_pct": _pct(row["near_miss_detection_rate_mean"]),
                    "task_success_pct": _pct(row["task_success_mean"]),
                    "task_success_ci_low_pct": _pct(row["task_success_ci_low"]),
                    "task_success_ci_high_pct": _pct(row["task_success_ci_high"]),
                    "pass_at_k_pct": _pct(match.get("task_success_pass_at_k_mean", row["task_success_mean"])) if match else _pct(row["task_success_mean"]),
                    "consistency_pct": _pct(match.get("success_consistency_rate", 1.0)) if match else 100.0,
                    "self_violation_pct": _pct(row["self_violation_rate_mean"]),
                    "parse_rate_pct": _pct(parse_match.get("parse_rate", 0.0)) if parse_match else 0.0,
                    "fallback_rate_pct": _pct(parse_match.get("fallback_rate", 0.0)) if parse_match else 0.0,
                }
            )
    return pd.DataFrame(rows)


def build_domain_table(runs: list[PilotRun]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run in runs:
        domain = _read_csv(run.report_dir / "stats" / "advanced_by_domain.csv")
        if domain.empty:
            continue
        domain = domain.copy()
        domain["agent_family"] = domain["agent"].astype(str).str.replace("_token_matched", "", regex=False)
        grouped = domain.groupby(["domain", "agent_family"], as_index=False).agg(
            n=("n", "sum"),
            task_success=("task_success", "mean"),
            cc_f1=("cc_f1", "mean"),
            near_miss_detection_rate=("near_miss_detection_rate", "mean"),
            self_violation_rate=("self_violation_rate", "mean"),
        )
        for _, row in grouped.iterrows():
            rows.append(
                {
                    "run_key": run.key,
                    "run": run.label,
                    "domain": row["domain"],
                    "agent_family": row["agent_family"],
                    "n_trials": int(row["n"]),
                    "task_success_pct": _pct(row["task_success"]),
                    "cc_f1_pct": _pct(row["cc_f1"]),
                    "near_miss_detection_pct": _pct(row["near_miss_detection_rate"]),
                    "self_violation_pct": _pct(row["self_violation_rate"]),
                }
            )
    return pd.DataFrame(rows)


def build_parse_table(runs: list[PilotRun]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run in runs:
        parse = _read_csv(run.report_dir / "parse" / "parse_transparency_by_model_agent.csv")
        if parse.empty:
            continue
        parse = parse.copy()
        parse["agent_family"] = parse["agent"].astype(str).str.replace("_token_matched", "", regex=False)
        for _, row in parse.iterrows():
            rows.append(
                {
                    "run_key": run.key,
                    "run": run.label,
                    "model": row["model"],
                    "agent": row["agent"],
                    "agent_family": row["agent_family"],
                    "n": int(row["n"]),
                    "parse_rate_pct": _pct(row["parse_rate"]),
                    "fallback_rate_pct": _pct(row["fallback_rate"]),
                    "mean_latency_s": round(float(row.get("mean_latency_s", 0.0)), 2),
                    "mean_total_tokens": round(float(row.get("mean_total_tokens", 0.0)), 1),
                }
            )
    return pd.DataFrame(rows)


def build_cost_table(runs: list[PilotRun]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run in runs:
        path = run.report_dir / "costs" / "api_cost_summary.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "run_key": run.key,
                "run": run.label,
                "calls": int(float(data.get("calls", 0))),
                "input_tokens": int(float(data.get("input_tokens", 0))),
                "output_tokens": int(float(data.get("output_tokens", 0))),
                "estimated_cost_usd": round(float(data.get("estimated_cost_usd", 0.0)), 4),
                "summed_provider_latency_hours": round(float(data.get("latency_s", 0.0)) / 3600, 2),
            }
        )
    return pd.DataFrame(rows)


def render_markdown(
    runs: list[PilotRun],
    comparison: pd.DataFrame,
    domain: pd.DataFrame,
    parse: pd.DataFrame,
    cost: pd.DataFrame,
    comparison_csv: Path,
    domain_csv: Path,
    parse_csv: Path,
    cost_csv: Path,
) -> str:
    standard = comparison[comparison["run_key"] == "standard_toolplan"]
    token = comparison[comparison["run_key"] == "token_matched"]
    repl = comparison[comparison["run_key"] == "replicates_5x"]
    spec_repl = repl[repl["agent_family"] == "spec_first"]

    lines: list[str] = [
        "# Pilot Findings",
        "",
        "Generated from the three DeepSeek pilot runs. This report is intentionally reviewer-conservative: it separates raw task success, token-budget controls, parse fallback risk, and repeated-attempt reliability.",
        "",
        "## Runs Compared",
        "",
    ]
    for run in runs:
        lines.append(f"- **{run.label}** (`{run.key}`): {run.notes}")
    lines.extend(
        [
            "",
            "Generated tables:",
            f"- `{comparison_csv.as_posix()}`",
            f"- `{domain_csv.as_posix()}`",
            f"- `{parse_csv.as_posix()}`",
            f"- `{cost_csv.as_posix()}`",
            "",
            "## Main Comparison",
            "",
            _markdown_table(_main_rows(comparison)),
            "",
            "## What Changed Across Pilots",
            "",
            _standard_vs_token_summary(standard, token),
            "",
            _replicate_summary(spec_repl),
            "",
            "## Parse Caveat",
            "",
            _parse_caveat(parse),
            "",
            "## Domain Failure Pattern",
            "",
            _domain_summary(domain),
            "",
            "## Reviewer-Safe Claims",
            "",
            "- DoneBench is measuring a separable capability: whether an agent can construct completion semantics before acting, reject near-miss completions, and then avoid violating its own DoneSpec during tool use.",
            "- Under the strict no-gold-leak tool-plan executor, the standard and 5-trial pilots show direct and plan-first baselines at zero task success, while spec-first opens a non-zero execution channel.",
            "- Token-matched controls show that raw task success is sensitive to prompt budget, so any claim that spec-first improves execution must be qualified by token budget.",
            "- The most robust current signal is reliability under repeated attempts: spec-first reaches non-zero pass@5, but with substantial inconsistency, which is itself a DoneBench failure mode.",
            "- Domain stratification matters: email and CRM currently show the clearest spec-first execution signal; file/document and sheet/database remain hard under the strict executor.",
            "",
            "## Unsafe Claims",
            "",
            "- Do not claim spec-first always wins. In the token-matched pilot, direct, plan-first, and spec-first are close on task success.",
            "- Do not claim DeepSeek Pro is uniformly better. Pro often has higher CC-F1 but lower or similar task success, and its spec-first parse fallback can be high.",
            "- Do not claim DoneBench is more realistic than WebArena, OSWorld, or WorkArena. The safe distinction is about completion-semantics evaluation, not broader environment realism.",
            "- Do not treat fallback-heavy cells as clean model-capability estimates without parse transparency.",
            "- Do not claim human audit is complete. The current audit gate still lacks double annotation.",
            "",
            "## Full-Run Decision",
            "",
            _full_run_decision(parse, domain, cost),
            "",
        ]
    )
    return "\n".join(lines)


def _main_rows(comparison: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "run",
        "model",
        "agent",
        "n_trials",
        "task_success_pct",
        "pass_at_k_pct",
        "consistency_pct",
        "near_miss_detection_pct",
        "parse_rate_pct",
    ]
    out = comparison[keep].copy()
    for col in keep[4:]:
        out[col] = out[col].map(lambda value: f"{value:.1f}")
    return out


def _standard_vs_token_summary(standard: pd.DataFrame, token: pd.DataFrame) -> str:
    if standard.empty or token.empty:
        return "Standard or token-matched pilot tables are missing, so the token-budget comparison is incomplete."
    standard_spec = _mean_metric(standard, "spec_first", "task_success_pct")
    token_spec = _mean_metric(token, "spec_first", "task_success_pct")
    token_direct = _mean_metric(token, "direct", "task_success_pct")
    token_plan = _mean_metric(token, "plan_first", "task_success_pct")
    standard_direct = _mean_metric(standard, "direct", "task_success_pct")
    standard_plan = _mean_metric(standard, "plan_first", "task_success_pct")
    return (
        f"In the standard pilot, direct and plan-first task success average {standard_direct:.1f}% and {standard_plan:.1f}%, "
        f"while spec-first averages {standard_spec:.1f}%. In the token-matched pilot, the gap collapses: direct, plan-first, "
        f"and spec-first average {token_direct:.1f}%, {token_plan:.1f}%, and {token_spec:.1f}%. This means prompt budget is a real "
        "confound for raw task success; the paper should emphasize completion-semantics and verifier behavior rather than a simple "
        "spec-first leaderboard story."
    )


def _replicate_summary(spec_repl: pd.DataFrame) -> str:
    if spec_repl.empty:
        return "The replicates pilot table is missing spec-first rows, so pass@5 cannot be interpreted."
    parts = []
    for _, row in spec_repl.iterrows():
        parts.append(
            f"{_pretty_model(row['model'])}: pass@1 {row['task_success_pct']:.1f}%, pass@{int(row['k'])} {row['pass_at_k_pct']:.1f}%, consistency {row['consistency_pct']:.1f}%"
        )
    return (
        "The 5-trial pilot turns the signal from a single-attempt score into a reliability measurement. "
        + "; ".join(parts)
        + ". The lift from pass@1 to pass@5 is meaningful, but the low consistency shows these are not stable solved tasks yet."
    )


def _parse_caveat(parse: pd.DataFrame) -> str:
    if parse.empty:
        return "Parse transparency outputs are missing."
    worst = parse.sort_values("fallback_rate_pct", ascending=False).head(3)
    worst_bits = [
        f"{row['run']} / {_pretty_model(row['model'])} / {row['agent']}: fallback {row['fallback_rate_pct']:.1f}%"
        for _, row in worst.iterrows()
    ]
    mean_fallback = parse["fallback_rate_pct"].mean()
    return (
        f"Across pilot cells, mean fallback is {mean_fallback:.1f}%. The riskiest cells are "
        + "; ".join(worst_bits)
        + ". These rows should stay in the paper with parse transparency attached, not hidden inside a single aggregate score."
    )


def _domain_summary(domain: pd.DataFrame) -> str:
    if domain.empty:
        return "Domain-stratified outputs are missing."
    repl_spec = domain[(domain["run_key"] == "replicates_5x") & (domain["agent_family"] == "spec_first")]
    if repl_spec.empty:
        repl_spec = domain[domain["agent_family"] == "spec_first"]
    grouped = repl_spec.groupby("domain", as_index=False).agg(task_success_pct=("task_success_pct", "mean"), cc_f1_pct=("cc_f1_pct", "mean"))
    ordered = grouped.sort_values("task_success_pct")
    hard = ", ".join(f"{row['domain']} ({row['task_success_pct']:.1f}%)" for _, row in ordered.head(2).iterrows())
    strong = ", ".join(f"{row['domain']} ({row['task_success_pct']:.1f}%)" for _, row in ordered.tail(2).sort_values("task_success_pct", ascending=False).iterrows())
    return (
        f"In the replicate pilot, spec-first succeeds most often in {strong}. The hardest domains are {hard}. "
        "This supports a domain-stratified analysis rather than one aggregate number: specification grounding helps most where the tool action can be operationalized, and fails where state edits require more precise non-oracle execution."
    )


def _full_run_decision(parse: pd.DataFrame, domain: pd.DataFrame, cost: pd.DataFrame) -> str:
    total_cost = cost["estimated_cost_usd"].sum() if not cost.empty else 0.0
    high_fallback = parse[parse["fallback_rate_pct"] >= 30.0] if not parse.empty else pd.DataFrame()
    hard_domains = []
    if not domain.empty:
        repl_spec = domain[(domain["run_key"] == "replicates_5x") & (domain["agent_family"] == "spec_first")]
        hard_domains = sorted(repl_spec[repl_spec["task_success_pct"] <= 1.0]["domain"].unique().tolist())

    reasons = [
        f"The pilots are cheap so far, with about ${total_cost:.2f} total estimated API cost across the generated pilot summaries.",
        "But a full run should not start immediately if the goal is a reviewer-safe paper claim.",
    ]
    if not high_fallback.empty:
        reasons.append(f"There are {len(high_fallback)} model-agent cells with fallback at or above 30%, which makes parse repair a live validity threat.")
    if hard_domains:
        reasons.append("The strict executor still has zero or near-zero spec-first success in these domains: " + ", ".join(hard_domains) + ".")
    reasons.append(
        "Decision: hold the full run until two gates are addressed: reduce or explicitly quarantine fallback-heavy cells, and complete at least AI-assisted plus targeted human audit for the high-risk task subset. The next API run should be a focused post-fix pilot, not the full matrix."
    )
    return " ".join(reasons)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _match_row(df: pd.DataFrame, model: str, agent: str) -> dict[str, Any]:
    if df.empty:
        return {}
    matched = df[(df["model"] == model) & (df["agent"] == agent)]
    if matched.empty:
        return {}
    return matched.iloc[0].to_dict()


def _pct(value: Any) -> float:
    return round(float(value) * 100.0, 2)


def _mean_metric(df: pd.DataFrame, agent_family: str, metric: str) -> float:
    group = df[df["agent_family"] == agent_family]
    if group.empty:
        return 0.0
    return float(group[metric].mean())


def _pretty_model(model: str) -> str:
    names = {
        "deepseek_v4_flash": "DeepSeek Flash",
        "deepseek_v4_pro": "DeepSeek Pro",
    }
    return names.get(str(model), str(model).replace("_", " "))


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows available._"
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(lines)
