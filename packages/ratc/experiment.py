"""Repeat seeded baselines and write measured comparison files."""

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from packages.ratc.fleet import ClientSpec
from packages.ratc.orchestrator import RunConfig, run_session

MODES = ("plain", "random", "static", "ratc")
RESEARCH_MODES = ("ratc", "reactive", "predictive", "bandit")


def comparison_fleet() -> List[ClientSpec]:
    """One client from each resource class, plus a second constrained device."""
    return [
        ClientSpec("ws-1", "workstation", 0.86),
        ClientSpec("mob-1", "mobile", 0.55),
        ClientSpec("iot-1", "iot_device", 0.22),
        ClientSpec("iot-2", "iot_device", 0.14),
    ]


def run_comparison(
    output_dir: Path,
    seeds: Sequence[int] = (7, 11),
    rounds: int = 2,
    modes: Iterable[str] = MODES,
) -> Dict[str, float]:
    """Run each mode and return final accuracy by mode, averaged over seeds."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, object]] = []
    for seed in seeds:
        for mode in modes:
            events = run_session(
                RunConfig(
                    mode=mode,
                    seed=int(seed),
                    num_rounds=rounds,
                    epochs=1,
                    clients=comparison_fleet(),
                )
            )
            for event in events:
                if event.get("type") != "ROUND_COMPLETED":
                    continue
                metrics = event["metrics"]
                rows.append(
                    {
                        "mode": mode,
                        "seed": int(seed),
                        "round": metrics["round"],
                        "accuracy": metrics["accuracy"],
                        "loss": metrics["loss"],
                        "latency_seconds": metrics["latency"],
                        "payload_bytes": metrics["payload_bytes"],
                        "epsilon": metrics["privacy_budget"],
                    }
                )
    _write_csv(output_dir / "comparison.csv", rows)
    summary = _summarize(rows)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (output_dir / "comparison.svg").write_text(_bar_svg(summary), encoding="utf-8")
    return summary


def _write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    fieldnames = [
        "mode",
        "seed",
        "round",
        "accuracy",
        "loss",
        "latency_seconds",
        "payload_bytes",
        "epsilon",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _summarize(rows: List[Dict[str, object]]) -> Dict[str, float]:
    finals: Dict[str, List[float]] = {}
    for row in rows:
        mode = str(row["mode"])
        finals.setdefault(mode, []).append(float(row["accuracy"]))
    summary: Dict[str, float] = {}
    for mode, values in finals.items():
        summary[mode] = sum(values) / len(values)
    return summary


def _bar_svg(summary: Dict[str, float]) -> str:
    width = 640
    height = 280
    bar_width = 80
    colors = ["#e08a45", "#3eafa0", "#d7b15a", "#8e97a8"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#10140f"/>',
        '<text x="24" y="32" fill="#efe7d6" font-family="sans-serif" '
        'font-size="18">Mean measured accuracy</text>',
    ]
    for index, (mode, accuracy) in enumerate(summary.items()):
        bar_height = max(4, int(accuracy * 180))
        x = 40 + index * 140
        y = 220 - bar_height
        color = colors[index % len(colors)]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" '
            f'height="{bar_height}" fill="{color}"/>'
        )
        label = f"{mode} {(accuracy * 100):.1f}%"
        parts.append(
            f'<text x="{x}" y="246" fill="#a3aa96" '
            f'font-family="sans-serif" font-size="13">{label}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)
