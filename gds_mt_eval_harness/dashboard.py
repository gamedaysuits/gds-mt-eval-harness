"""
Dashboard Generator — produces a self-contained, branded HTML evaluation dashboard.

Architecture:
  - CSS/JS live in _dashboard_css.py and _dashboard_js.py for maintainability
  - GDS logo is embedded as a base64 PNG (64px, ~9KB)
  - All report data is embedded as JSON so the file works offline
  - The generator supports both individual report files and directory scanning

Directory mode (dynamic):
  Pass a directory path and the generator will find all *_report.json files,
  include them all, and produce a multi-run comparison dashboard.
"""

import json
import os
import sys
import base64
import glob
from pathlib import Path

from ._dashboard_css import CSS
from ._dashboard_js import JS


# ── Logo ─────────────────────────────────────────────────────────────────────
# The GDS suit logo, pre-encoded as base64 PNG.
# Generated from the brand vector at 64x64px for minimal file overhead.
LOGO_PATH = Path(__file__).parent / "assets" / "gds_logo_64.png"


def _load_logo_b64() -> str:
    """Load logo from assets dir and return base64 string, or empty string."""
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    return ""


# ── Report Loading ───────────────────────────────────────────────────────────
def load_reports(paths: list[str]) -> list[dict]:
    """
    Load report JSON files from a list of paths.
    Each path can be:
      - A specific *_report.json file
      - A directory (scanned for all *_report.json files)
    """
    reports = []
    seen = set()

    for p in paths:
        if os.path.isdir(p):
            # Directory mode: find all report files
            pattern = os.path.join(p, "*_report.json")
            for f in sorted(glob.glob(pattern)):
                if f not in seen:
                    seen.add(f)
                    reports.append(_load_one(f))
        elif os.path.isfile(p):
            if p not in seen:
                seen.add(p)
                reports.append(_load_one(p))
        else:
            print(f"  Warning: skipping '{p}' — not found", file=sys.stderr)

    return reports


def _load_one(path: str) -> dict:
    """Load a single report JSON file."""
    with open(path) as f:
        data = json.load(f)

    # Inject the run name from config if available, or derive from filename
    config = data.get("config", {})
    if not config.get("run_name"):
        # Derive from filename: run_YYYYMMDD_..._name_report.json -> extract name
        base = os.path.basename(path).replace("_report.json", "")
        config["run_name"] = base
        data["config"] = config

    return data


# ── HTML Assembly ────────────────────────────────────────────────────────────
def generate(reports: list[dict], output_path: str = "dashboard.html") -> str:
    """
    Generate the dashboard HTML and write to output_path.

    Returns the output path for caller convenience.
    """
    logo_b64 = _load_logo_b64()
    logo_img = (
        f'<img src="data:image/png;base64,{logo_b64}" class="header-logo" alt="GDS">'
        if logo_b64
        else '<div class="header-logo" style="background:var(--gds-royal);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.1rem;color:#fff">GDS</div>'
    )

    # Read version from pyproject.toml
    version = "0.1.0"
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().splitlines():
            if line.strip().startswith("version"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

    # Determine generation timestamp
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build the report JSON payload
    data_json = json.dumps(reports, ensure_ascii=False, separators=(",", ":"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GDS MT Eval Dashboard</title>
<style>{CSS}</style>
</head>
<body>

<!-- ── Header ──────────────────────────────────────── -->
<div class="header">
    {logo_img}
    <div class="header-text">
        <div class="header-title">MT Eval Harness <span style="font-size:0.7rem;opacity:0.5">v{version}</span></div>
        <div class="header-sub">Game Day Suits · {len(reports)} run{"s" if len(reports) != 1 else ""} · {ts}</div>
    </div>
</div>

<div class="main">

<!-- ── Run Tabs ────────────────────────────────────── -->
<div class="section" style="margin-bottom:0;border-bottom:none;border-bottom-left-radius:0;border-bottom-right-radius:0">
    <div id="run-tabs" class="run-tabs"></div>
</div>

<!-- ── Metric Cards ───────────────────────────────── -->
<div class="section" style="border-top-left-radius:0;border-top-right-radius:0;border-top:none">
    <div class="section-body">
        <div id="metric-cards" class="metric-grid"></div>
    </div>
</div>

<!-- ── Run Comparison Table ───────────────────────── -->
<div class="section" id="compare-section">
    <div class="section-head"><span class="section-title">Run Comparison</span></div>
    <div class="section-body" style="overflow-x:auto"><div id="compare-table"></div></div>
</div>

<!-- ── SVG Bar Chart (multi-run) ─────────────────── -->
<div class="section" id="barchart-section">
    <div class="section-head"><span class="section-title">Performance Overview</span></div>
    <div class="section-body"><div id="barchart" class="chart-wrap"></div></div>
</div>

<!-- ── Segment Breakdown ─────────────────────────── -->
<div class="section" id="segment-section">
    <div class="section-head"><span class="section-title">Segment Breakdown</span></div>
    <div class="section-body"><div id="segment-bars" class="bar-group"></div></div>
</div>

<!-- ── Segment × Run Matrix ──────────────────────── -->
<div class="section" id="seg-compare-section">
    <div class="section-head"><span class="section-title">Segment × Run Matrix</span></div>
    <div class="section-body" style="overflow-x:auto"><div id="seg-compare-table"></div></div>
</div>

<!-- ── chrF++ Distribution ───────────────────────── -->
<div class="section" id="histogram-section">
    <div class="section-head"><span class="section-title">chrF++ Distribution</span></div>
    <div class="section-body"><div id="histogram" class="chart-wrap"></div></div>
</div>

<!-- ── View Toggle ───────────────────────────────── -->
<div class="section" style="margin-bottom:0;border-bottom:none;border-bottom-left-radius:0;border-bottom-right-radius:0">
    <div class="section-head">
        <span class="section-title">Translation Results</span>
    </div>
    <div class="view-toggle">
        <button class="view-toggle-btn active" data-view="explorer">Entry Explorer</button>
        <button class="view-toggle-btn" data-view="sidebyside">Side-by-Side Comparison</button>
    </div>
</div>

<!-- ── Entry Explorer ─────────────────────────────── -->
<div class="section" id="explorer-section" style="border-top:none;border-top-left-radius:0;border-top-right-radius:0">
    <div class="explorer-bar">
        <input type="text" id="search-box" class="search-box" placeholder="Search source, target, or predicted text…">
        <select id="filter-seg" class="filter-sel"><option value="">All segments</option></select>
        <select id="filter-match" class="filter-sel">
            <option value="">All results</option>
            <option value="exact">Exact match</option>
            <option value="miss">Misses</option>
            <option value="error">Errors</option>
        </select>
        <span id="entry-count" class="count-label"></span>
    </div>
    <div id="entry-list" class="entry-scroll"></div>
</div>

<!-- ── Side-by-Side Comparison ────────────────────── -->
<div class="section" id="sbs-section" style="border-top:none;border-top-left-radius:0;border-top-right-radius:0;display:none">
    <div class="explorer-bar">
        <input type="text" id="sbs-search" class="search-box" placeholder="Search entries…">
        <select id="sbs-filter-seg" class="filter-sel"><option value="">All segments</option></select>
        <select id="sbs-filter-match" class="filter-sel">
            <option value="">All entries</option>
            <option value="disagree">Runs disagree</option>
            <option value="all_miss">All miss</option>
            <option value="all_exact">All exact</option>
        </select>
        <span id="sbs-count" class="count-label"></span>
    </div>
    <div id="sbs-table-wrap" class="sbs-wrap"></div>
</div>

</div><!-- /main -->

<div class="footer">
    <div>GDS MT Eval Harness v{version} · Apache-2.0 License</div>
    <div class="license-bar">
        <span><a href="https://github.com/gamedaysuits/gds-mt-eval-harness" target="_blank">GitHub</a></span>
        <span>·</span>
        <span><a href="https://gamedaysuits.ca" target="_blank">gamedaysuits.ca</a></span>
        <span>·</span>
        <span>Generated {ts}</span>
    </div>
</div>

<script>window.__REPORTS = {data_json};</script>
<script>{JS}</script>

</body>
</html>"""

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    return output_path


# ── CLI Entry Point (standalone usage) ───────────────────────────────────────
def main():
    """Usage: python -m gds_mt_eval_harness.dashboard <report_or_dir> [...] [-o out.html]"""
    args = sys.argv[1:]
    output = "dashboard.html"
    paths = []

    i = 0
    while i < len(args):
        if args[i] in ("-o", "--output") and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        else:
            paths.append(args[i])
            i += 1

    if not paths:
        print("Usage: dashboard <report.json or dir> [...] [-o output.html]")
        sys.exit(1)

    reports = load_reports(paths)
    if not reports:
        print("No reports found.")
        sys.exit(1)

    out = generate(reports, output)
    print(f"  Dashboard written to: {out}")
    print(f"  Open in browser: file://{os.path.abspath(out)}")


if __name__ == "__main__":
    main()
