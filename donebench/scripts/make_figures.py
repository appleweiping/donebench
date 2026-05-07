from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def make_figures(results_root: Path, figures_root: Path) -> list[Path]:
    figures_root.mkdir(parents=True, exist_ok=True)
    by_agent_path = results_root / "by_agent.csv"
    by_domain_path = results_root / "by_domain.csv"
    made: list[Path] = []
    if by_agent_path.exists():
        df = pd.read_csv(by_agent_path)
        fig, ax = plt.subplots(figsize=(7, 4))
        x = range(len(df))
        ax.bar([i - 0.18 for i in x], df["cc_f1"], width=0.36, label="CC-F1")
        ax.bar([i + 0.18 for i in x], df["task_success"], width=0.36, label="Task success")
        ax.set_xticks(list(x), df["agent"], rotation=20)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Mean score")
        ax.legend()
        fig.tight_layout()
        out = figures_root / "main_results_by_agent.png"
        fig.savefig(out, dpi=160)
        plt.close(fig)
        made.append(out)
    if by_domain_path.exists():
        df = pd.read_csv(by_domain_path)
        pivot = df.pivot_table(index="domain", columns="agent", values="near_miss_detection_rate", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(7, 4))
        pivot.plot(kind="bar", ax=ax)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Near-miss detection")
        fig.tight_layout()
        out = figures_root / "near_miss_by_domain.png"
        fig.savefig(out, dpi=160)
        plt.close(fig)
        made.append(out)
    return made
