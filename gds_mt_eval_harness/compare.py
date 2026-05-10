"""
Run Comparator — Compare multiple TestReport files side by side.

Generates a structured comparison showing how different configs
perform on the same corpus entries. Useful for answering:
    - "Did tool-calling improve accuracy?"
    - "How does Gemini compare to Claude on difficulty 5?"
    - "What's the cost/accuracy tradeoff between models?"

Also identifies per-entry regressions and improvements between runs.
"""

from __future__ import annotations

import json
from pathlib import Path


def compare_reports(report_paths: list[str | Path]) -> dict:
    """Load and compare multiple TestReport files.

    Args:
        report_paths: Paths to TestReport JSON files (from tester.py).

    Returns:
        Comparison dict with overall metrics, per-entry diffs, etc.
    """
    reports = []
    for p in report_paths:
        path = Path(p)
        if not path.exists():
            print(f"  WARNING: Report not found: {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        reports.append(data)

    if len(reports) < 2:
        print("  Need at least 2 reports to compare")
        return {"error": "Insufficient reports"}

    # --- Overall comparison table ---
    comparison_rows = []
    for r in reports:
        config = r.get("config", {})
        overall = r.get("overall", {})
        comparison_rows.append({
            "run_id": r.get("run_id", "?"),
            "model": config.get("model", "?"),
            "prompt": config.get("prompt_version", "?"),
            "tools": config.get("tools_enabled", False),
            "fst_gate": config.get("fst_gate_enabled", False),
            "batch_size": config.get("batch_size", 1),
            "entries": overall.get("evaluated", 0),
            "exact_match": overall.get("exact_match_rate", 0),
            "equivalent": overall.get("equivalent_match_rate", 0),
            "corpus_chrf": overall.get("corpus_chrf", 0),
            "avg_fst_validity": overall.get("avg_fst_validity", 0),
            "total_cost": overall.get("total_cost_usd", 0),
            "avg_latency": overall.get("avg_latency_s", 0),
        })

    # --- Per-entry diff (first vs last run) ---
    first_entries = {e["id"]: e for e in reports[0].get("entries", [])}
    last_entries = {e["id"]: e for e in reports[-1].get("entries", [])}

    regressions = []  # Entries that got worse
    improvements = []  # Entries that got better
    common_ids = set(first_entries.keys()) & set(last_entries.keys())

    for eid in sorted(common_ids):
        first = first_entries[eid]
        last = last_entries[eid]

        # Check if match status changed
        first_match = first.get("exact_match") or first.get("equivalent_match")
        last_match = last.get("exact_match") or last.get("equivalent_match")

        if first_match and not last_match:
            regressions.append({
                "id": eid,
                "english": first.get("english", ""),
                "expected": first.get("expected", ""),
                "first_predicted": first.get("predicted", ""),
                "last_predicted": last.get("predicted", ""),
            })
        elif not first_match and last_match:
            improvements.append({
                "id": eid,
                "english": first.get("english", ""),
                "expected": first.get("expected", ""),
                "first_predicted": first.get("predicted", ""),
                "last_predicted": last.get("predicted", ""),
            })

    comparison = {
        "run_count": len(reports),
        "overall_comparison": comparison_rows,
        "regressions": regressions,
        "improvements": improvements,
        "regression_count": len(regressions),
        "improvement_count": len(improvements),
    }

    return comparison


def run_compare(
    log_paths: list[str],
    output_path: str | None = None,
):
    """CLI entry point for the compare subcommand.

    Accepts either RunLog or TestReport JSON files. If given RunLogs,
    it looks for corresponding _report.json files.
    """
    # Resolve report paths
    report_paths = []
    for lp in log_paths:
        path = Path(lp)
        # Try as-is first (might be a report)
        if path.exists():
            # Check if it has "overall" key (report) or "results" key (run log)
            data = json.loads(path.read_text(encoding="utf-8"))
            if "overall" in data:
                report_paths.append(path)
            elif "results" in data:
                # It's a RunLog — look for corresponding report
                report_path = path.with_name(path.stem + "_report.json")
                if report_path.exists():
                    report_paths.append(report_path)
                else:
                    print(f"  No report for {path.name} — run 'test' first")
            continue
        print(f"  WARNING: File not found: {lp}")

    if len(report_paths) < 2:
        print("  Need at least 2 reports to compare. Run 'test' on your logs first.")
        return

    comparison = compare_reports(report_paths)

    # Print comparison table
    print("\n" + "=" * 80)
    print("RUN COMPARISON")
    print("=" * 80)

    rows = comparison["overall_comparison"]
    print(f"\n  {'Run ID':40s} {'Model':18s} {'Exact':>7s} {'Equiv':>7s} "
          f"{'chrF++':>7s} {'FST%':>6s} {'Cost':>8s}")
    print(f"  {'-'*40} {'-'*18} {'-----':>7s} {'-----':>7s} "
          f"{'------':>7s} {'----':>6s} {'----':>8s}")

    for r in rows:
        flags = []
        if r["tools"]:
            flags.append("T")
        if r["fst_gate"]:
            flags.append("G")
        flag_str = f" [{','.join(flags)}]" if flags else ""

        print(
            f"  {r['run_id'][:40]:40s} "
            f"{r['model']:18s} "
            f"{r['exact_match']:>6.1%} "
            f"{r['equivalent']:>6.1%} "
            f"{r['corpus_chrf']:>7.1f} "
            f"{r['avg_fst_validity']:>5.1%} "
            f"${r['total_cost']:>7.4f}"
            f"{flag_str}"
        )

    # Regressions and improvements
    regs = comparison["regressions"]
    imps = comparison["improvements"]

    if imps:
        print(f"\n  IMPROVEMENTS ({len(imps)} entries now correct):")
        for item in imps[:10]:
            print(f"    #{item['id']:3d}: {item['english'][:50]}")
            print(f"         was: {item['first_predicted'][:50]}")
            print(f"         now: {item['last_predicted'][:50]}")

    if regs:
        print(f"\n  REGRESSIONS ({len(regs)} entries now wrong):")
        for item in regs[:10]:
            print(f"    #{item['id']:3d}: {item['english'][:50]}")
            print(f"         was: {item['first_predicted'][:50]}")
            print(f"         now: {item['last_predicted'][:50]}")

    # Write output
    if output_path is None:
        output_path = "eval/logs/harness/comparison.json"
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n  Comparison written to: {out}")
    print("=" * 80)
