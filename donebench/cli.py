from __future__ import annotations

from pathlib import Path

import typer
import yaml
from rich.console import Console

from donebench.core.config import load_experiment, load_models
from donebench.core.validation import audit_tasks, validate_tasks
from donebench.scripts.aggregate_results import aggregate as aggregate_results
from donebench.scripts.advanced_stats import write_advanced_stats
from donebench.scripts.annotation_agreement import write_annotation_agreement
from donebench.scripts.ai_audit import run_ai_audit
from donebench.scripts.audit_gate import write_audit_gate
from donebench.scripts.cost_report import write_cost_report
from donebench.scripts.action_diagnostics import write_action_diagnostics
from donebench.scripts.experiment_pipeline import run_experiment_pipeline
from donebench.scripts.export_openreview_package import export_package
from donebench.scripts.failure_mining import mine_failures
from donebench.scripts.generate_seed_tasks import generate
from donebench.scripts.human_audit_queue import write_human_audit_queue
from donebench.scripts.make_figures import make_figures as make_figures_impl
from donebench.scripts.parse_transparency import write_parse_transparency
from donebench.scripts.quality_audit import quality_audit
from donebench.scripts.repro_manifest import write_repro_manifest
from donebench.scripts.readiness_report import write_readiness_report
from donebench.scripts.run_experiments import run as run_experiment
from donebench.scripts.run_experiments import run_matrix
from donebench.scripts.run_experiments import run_matrix_streaming
from donebench.scripts.run_experiments import select_tasks
from donebench.scripts.run_experiments import append_jsonl
from donebench.scripts.run_experiments import write_manifest
from donebench.scripts.run_experiments import write_jsonl

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def generate_tasks(root: Path = typer.Argument(Path("data/tasks"))) -> None:
    generate(root)
    console.print(f"Generated tasks under {root}")


@app.command()
def validate(root: Path = typer.Argument(Path("data/tasks"))) -> None:
    tasks, errors = validate_tasks(root)
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    console.print(f"Validated {len(tasks)} tasks")


@app.command("audit-tasks")
def audit_tasks_cmd(root: Path = typer.Argument(Path("data/tasks"))) -> None:
    counts, errors = audit_tasks(root)
    for domain, count in sorted(counts.items()):
        console.print(f"{domain}: {count}")
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    console.print("Task audit passed")


@app.command()
def run(
    config: Path = typer.Option(Path("configs/experiments.yaml"), "--config"),
    split: str = typer.Option("dev", "--split"),
    agent: str = typer.Option("heuristic", "--agent"),
    model: str = typer.Option("mock", "--model"),
    limit: int | None = typer.Option(None, "--limit"),
) -> None:
    cfg = {}
    if config.exists():
        cfg = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
    task_root = Path(cfg.get("task_root", "data/tasks"))
    rows = run_experiment(task_root, split=split, agent_name=agent, model=model, limit=limit)
    output = Path("results") / f"{split}_{agent}_{model}.jsonl"
    write_jsonl(rows, output)
    console.print(f"Wrote {len(rows)} trials to {output}")


@app.command("run-matrix")
def run_matrix_cmd(
    config: Path = typer.Option(Path("configs/experiments.yaml"), "--config"),
    models: Path = typer.Option(Path("configs/models.yaml"), "--models"),
    suite: str | None = typer.Option(None, "--suite"),
    split: str | None = typer.Option(None, "--split"),
    limit: int | None = typer.Option(None, "--limit"),
    output: Path = typer.Option(Path("results/matrix.jsonl"), "--output"),
    append: bool = typer.Option(False, "--append", help="Append rows instead of replacing the output file."),
    streaming: bool = typer.Option(True, "--streaming/--no-streaming", help="Write results as each agent/model/trial finishes."),
    resume: bool = typer.Option(False, "--resume", help="Skip trials already present in the output JSONL."),
    max_workers: int = typer.Option(1, "--max-workers", min=0, help="Number of concurrent independent API trials. Use 0 for suite recommendation."),
) -> None:
    try:
        exp = load_experiment(config).with_suite(suite)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    model_configs = load_models(models)
    if output == Path("results/matrix.jsonl") and suite:
        output = Path("results") / f"{suite}.jsonl"
    if streaming:
        resolved_workers = exp.resolved_max_workers(max_workers)
        num_rows, skipped = run_matrix_streaming(
            exp,
            model_configs,
            output,
            split=split,
            limit=limit,
            append=append,
            resume=resume,
            max_workers=resolved_workers,
        )
        rows = []
    else:
        rows, skipped = run_matrix(exp, model_configs, split=split, limit=limit)
        if append:
            append_jsonl(rows, output)
        else:
            write_jsonl(rows, output)
        num_rows = len(rows)
    write_manifest(output.with_suffix(".manifest.json"), [{"_count": num_rows}], skipped, {"config": str(config), "models": str(models)})
    console.print(f"Wrote {num_rows} trials to {output}")
    if skipped:
        console.print(f"Skipped {len(skipped)} agent/model combinations; see {output.with_suffix('.manifest.json')}")


@app.command("plan-matrix")
def plan_matrix_cmd(
    config: Path = typer.Option(Path("configs/experiments.yaml"), "--config"),
    models: Path = typer.Option(Path("configs/models.yaml"), "--models"),
    suite: str | None = typer.Option(None, "--suite"),
    split: str | None = typer.Option(None, "--split"),
    limit: int | None = typer.Option(None, "--limit"),
) -> None:
    try:
        exp = load_experiment(config).with_suite(suite)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    model_configs = load_models(models)
    task_root = Path(exp.task_root)
    tasks, errors = validate_tasks(task_root)
    if errors:
        for error in errors[:20]:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    actual_split = split or exp.default_split
    selected = [task for task in tasks if task.audit.split == actual_split]
    if limit:
        selected = select_tasks(selected, limit)
    enabled_models = [model for model in exp.models if model_configs.get(model) and model_configs[model].enabled]
    planned = len(selected) * len(exp.agents) * len(enabled_models) * exp.trials_per_model
    console.print(
        {
            "suite": suite or "default",
            "split": actual_split,
            "tasks": len(selected),
            "agents": exp.agents,
            "models": enabled_models,
            "trials_per_model": exp.trials_per_model,
            "planned_trials": planned,
        }
    )


@app.command()
def aggregate(root: Path = typer.Argument(Path("results"))) -> None:
    summary = aggregate_results(root)
    console.print(summary)


@app.command("advanced-stats")
def advanced_stats_cmd(
    input_path: Path = typer.Argument(...),
    output_dir: Path = typer.Argument(Path("reports/stats")),
    model_a: str = typer.Option("deepseek_v4_flash", "--model-a"),
    model_b: str = typer.Option("deepseek_v4_pro", "--model-b"),
) -> None:
    summary = write_advanced_stats(input_path, output_dir, model_a=model_a, model_b=model_b)
    console.print(summary)


@app.command("quality-audit")
def quality_audit_cmd(root: Path = typer.Argument(Path("data/tasks")), output_dir: Path = typer.Argument(Path("reports/quality"))) -> None:
    summary = quality_audit(root, output_dir)
    console.print(summary)


@app.command("readiness-report")
def readiness_report_cmd(
    root: Path = typer.Argument(Path("data/tasks")),
    quality_summary: Path = typer.Option(Path("reports/quality/task_quality_summary.json"), "--quality-summary"),
    output: Path = typer.Argument(Path("reports/readiness_report.json")),
) -> None:
    summary = write_readiness_report(root, quality_summary, output)
    console.print(summary)


@app.command("mine-failures")
def mine_failures_cmd(input_path: Path = typer.Argument(...), output_dir: Path = typer.Argument(Path("reports/failures")), top_k: int = typer.Option(25, "--top-k")) -> None:
    summary = mine_failures(input_path, output_dir, top_k=top_k)
    console.print(summary)


@app.command("cost-report")
def cost_report_cmd(
    input_path: Path = typer.Argument(...),
    output_dir: Path = typer.Argument(Path("reports/costs")),
    task_root: Path = typer.Option(Path("data/tasks"), "--task-root"),
    fallback_output_tokens: int = typer.Option(1200, "--fallback-output-tokens"),
) -> None:
    summary = write_cost_report(input_path, output_dir, task_root=task_root, fallback_output_tokens=fallback_output_tokens)
    console.print(summary)


@app.command("parse-transparency")
def parse_transparency_cmd(
    input_path: Path = typer.Argument(...),
    output_dir: Path = typer.Argument(Path("reports/parse_transparency")),
) -> None:
    summary = write_parse_transparency(input_path, output_dir)
    console.print(summary)


@app.command("action-diagnostics")
def action_diagnostics_cmd(
    input_path: Path = typer.Argument(...),
    output_dir: Path = typer.Argument(Path("reports/action_diagnostics")),
) -> None:
    summary = write_action_diagnostics(input_path, output_dir)
    console.print(summary)


@app.command("experiment-pipeline")
def experiment_pipeline_cmd(
    suite: str = typer.Argument(...),
    output: Path | None = typer.Option(None, "--output"),
    report_root: Path = typer.Option(Path("reports"), "--report-root"),
    config: Path = typer.Option(Path("configs/experiments.yaml"), "--config"),
    models: Path = typer.Option(Path("configs/models.yaml"), "--models"),
    split: str | None = typer.Option(None, "--split"),
    limit: int | None = typer.Option(None, "--limit"),
    max_workers: int = typer.Option(0, "--max-workers", min=0),
    resume: bool = typer.Option(True, "--resume/--no-resume"),
    postprocess_only: bool = typer.Option(False, "--postprocess-only"),
) -> None:
    summary = run_experiment_pipeline(
        suite,
        output=output,
        report_root=report_root,
        config_path=config,
        models_path=models,
        split=split,
        limit=limit,
        max_workers=max_workers,
        resume=resume,
        postprocess_only=postprocess_only,
    )
    console.print(summary)


@app.command("repro-manifest")
def repro_manifest_cmd(output: Path = typer.Argument(Path("reports/repro_manifest.json")), results: Path | None = typer.Option(None, "--results")) -> None:
    manifest = write_repro_manifest(output, results)
    console.print(manifest)


@app.command("human-audit-queue")
def human_audit_queue_cmd(root: Path = typer.Argument(Path("data/tasks")), output: Path = typer.Argument(Path("annotation/human_audit_queue.jsonl")), per_domain: int = typer.Option(10, "--per-domain")) -> None:
    count = write_human_audit_queue(root, output, per_domain=per_domain)
    console.print(f"Wrote {count} audit items to {output}")


@app.command("ai-audit")
def ai_audit_cmd(
    input_path: Path = typer.Argument(Path("annotation/human_audit_queue.jsonl")),
    output_dir: Path = typer.Argument(Path("reports/audit")),
    task_root: Path = typer.Option(Path("data/tasks"), "--task-root"),
    models: Path = typer.Option(Path("configs/models.yaml"), "--models"),
    model: str = typer.Option("mock", "--model"),
    limit: int | None = typer.Option(None, "--limit"),
    require_live: bool = typer.Option(False, "--require-live", help="Fail instead of falling back when the configured model cannot be used."),
) -> None:
    summary = run_ai_audit(
        input_path,
        output_dir,
        task_root=task_root,
        models_path=models,
        model_id=model,
        limit=limit,
        require_live=require_live,
    )
    console.print(summary)


@app.command("annotation-agreement")
def annotation_agreement_cmd(
    input_path: Path = typer.Argument(Path("annotation/human_audit_queue.jsonl")),
    output_dir: Path = typer.Argument(Path("reports/audit")),
) -> None:
    summary = write_annotation_agreement(input_path, output_dir)
    console.print(summary)


@app.command("audit-gate")
def audit_gate_cmd(
    output: Path = typer.Argument(Path("reports/audit_gate.json")),
    annotation_path: Path = typer.Option(Path("annotation/human_audit_queue.jsonl"), "--annotation"),
    ai_audit_path: Path = typer.Option(Path("reports/audit/ai_audit_opinions.jsonl"), "--ai-audit"),
) -> None:
    summary = write_audit_gate(output, annotation_path=annotation_path, ai_audit_path=ai_audit_path)
    console.print(summary)


@app.command("make-figures")
def make_figures(root: Path = typer.Argument(Path("results")), figures: Path = typer.Argument(Path("paper/figures"))) -> None:
    made = make_figures_impl(root, figures)
    for path in made:
        console.print(path)


@app.command("export-paper-package")
def export_paper_package() -> None:
    path = export_package(Path("."))
    console.print(f"Wrote {path}")


if __name__ == "__main__":
    app()
