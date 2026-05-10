"""
Dashboard Generator — Produces a self-contained interactive HTML dashboard.

Takes one or more TestReport JSON files and produces a single HTML file
with zero external dependencies. The dashboard embeds all data inline
and uses vanilla JS/CSS for:
    - Overall metric cards
    - Run comparison table
    - Per-segment breakdown
    - Per-difficulty breakdown
    - Searchable entry explorer with full drill-down
    - Plugin metric distribution charts (auto-detected)
    - Cost/latency analysis

Design decisions:
    - Zero dependencies: no CDN, no framework, no build step.
      The HTML file is fully self-contained and can be opened
      in any browser, shared via email, or committed to git.
    - Data is embedded as a JSON blob in a <script> tag.
    - CSS variables for theming (dark mode default).
    - All interactions are vanilla JS event handlers.
    - Plugin metrics are rendered dynamically — the dashboard
      auto-detects any plugin_metrics in the report and renders
      them without hardcoded field references.
"""

from __future__ import annotations

import json
from pathlib import Path


def generate(log_paths: list[str], output_path: str = "eval/harness/dashboard_output.html"):
    """Generate an interactive HTML dashboard from TestReport files.

    Args:
        log_paths: Paths to TestReport or RunLog JSON files.
        output_path: Where to write the HTML file.
    """
    # Load all reports
    reports = []
    for lp in log_paths:
        path = Path(lp)
        if not path.exists():
            print(f"  WARNING: Not found: {lp}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        # Accept both RunLog and TestReport
        if "overall" in data:
            reports.append(data)
        elif "results" in data:
            # It's a RunLog — look for corresponding report
            rp = path.with_name(path.stem + "_report.json")
            if rp.exists():
                reports.append(json.loads(rp.read_text(encoding="utf-8")))
            else:
                print(f"  No report for {path.name} — run 'test' first")

    if not reports:
        print("  No reports to dashboard. Run 'test' on your logs first.")
        return

    # Embed data as JSON
    embedded_data = json.dumps(reports, ensure_ascii=False)

    html = _build_html(embedded_data, len(reports))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  Dashboard written to: {out}")
    print(f"  Open in browser: file://{out.resolve()}")


def _build_html(embedded_json: str, report_count: int) -> str:
    """Build the complete HTML string."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Translation Harness — Evaluation Dashboard</title>
    <style>
{_CSS}
    </style>
</head>
<body>
    <header class="header">
        <h1>Translation Harness Dashboard</h1>
        <p class="header-sub">{report_count} run(s) loaded</p>
    </header>

    <main class="main">
        <!-- Overall metrics -->
        <section id="metrics-section" class="section">
            <h2>Overall Metrics</h2>
            <div id="metric-cards" class="metric-cards"></div>
        </section>

        <!-- Run comparison -->
        <section id="comparison-section" class="section" style="display:none">
            <h2>Run Comparison</h2>
            <div id="comparison-table-wrap" class="table-wrap"></div>
        </section>

        <!-- Segment breakdown -->
        <section id="segment-section" class="section">
            <h2>Per-Segment Breakdown</h2>
            <div id="segment-table-wrap" class="table-wrap"></div>
        </section>

        <!-- Difficulty breakdown -->
        <section id="difficulty-section" class="section">
            <h2>Per-Difficulty Breakdown</h2>
            <div id="difficulty-table-wrap" class="table-wrap"></div>
        </section>

        <!-- Plugin metrics (dynamically populated) -->
        <section id="plugin-section" class="section" style="display:none">
            <h2>Plugin Metrics</h2>
            <div id="plugin-charts" class="bar-chart"></div>
        </section>

        <!-- Entry explorer -->
        <section id="explorer-section" class="section">
            <h2>Entry Explorer</h2>
            <div class="explorer-controls">
                <input type="text" id="search-input" placeholder="Search source or target text..."
                       class="search-input">
                <select id="filter-segment" class="filter-select">
                    <option value="">All segments</option>
                </select>
                <select id="filter-match" class="filter-select">
                    <option value="">All matches</option>
                    <option value="exact">Exact only</option>
                    <option value="miss">Misses only</option>
                    <option value="error">Errors only</option>
                </select>
                <span id="entry-count" class="entry-count"></span>
            </div>
            <div id="entry-list" class="entry-list"></div>
        </section>
    </main>

    <script>
    // Embedded report data
    const REPORTS = {embedded_json};

{_JS}
    </script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_CSS = """
:root {
    --bg-primary: #0f1117;
    --bg-secondary: #1a1d27;
    --bg-card: #21242f;
    --bg-hover: #2a2e3a;
    --text-primary: #e4e6eb;
    --text-secondary: #9ca0ab;
    --text-muted: #6b7080;
    --accent-green: #4ade80;
    --accent-blue: #60a5fa;
    --accent-amber: #fbbf24;
    --accent-red: #f87171;
    --accent-purple: #a78bfa;
    --border: #2a2e3a;
    --radius: 8px;
    --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font);
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    padding: 24px;
}

.header {
    text-align: center;
    margin-bottom: 32px;
    padding: 24px;
    background: linear-gradient(135deg, #1a1d27 0%, #21242f 100%);
    border-radius: var(--radius);
    border: 1px solid var(--border);
}

.header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-sub {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 4px;
}

.section {
    margin-bottom: 32px;
    background: var(--bg-secondary);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    padding: 24px;
}

.section h2 {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--text-primary);
}

/* Metric cards */
.metric-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
}

.metric-card {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 16px;
    border: 1px solid var(--border);
    text-align: center;
}

.metric-card .label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-card .value {
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 4px;
    font-family: var(--font-mono);
}

.metric-card .value.green { color: var(--accent-green); }
.metric-card .value.blue { color: var(--accent-blue); }
.metric-card .value.amber { color: var(--accent-amber); }
.metric-card .value.red { color: var(--accent-red); }
.metric-card .value.purple { color: var(--accent-purple); }

/* Tables */
.table-wrap { overflow-x: auto; }

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}

th, td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}

th {
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

td { color: var(--text-primary); }

tr:hover td { background: var(--bg-hover); }

td.num {
    text-align: right;
    font-family: var(--font-mono);
    font-size: 0.82rem;
}

/* Bar charts */
.bar-chart { display: flex; flex-direction: column; gap: 8px; }

.bar-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.bar-label {
    width: 200px;
    font-size: 0.82rem;
    color: var(--text-secondary);
    text-align: right;
    flex-shrink: 0;
}

.bar-track {
    flex: 1;
    height: 24px;
    background: var(--bg-card);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}

.bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}

.bar-value {
    width: 60px;
    font-size: 0.82rem;
    font-family: var(--font-mono);
    color: var(--text-primary);
    text-align: right;
    flex-shrink: 0;
}

/* Explorer */
.explorer-controls {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
    align-items: center;
}

.search-input {
    flex: 1;
    min-width: 200px;
    padding: 8px 12px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 0.85rem;
    font-family: var(--font);
}

.search-input:focus {
    outline: none;
    border-color: var(--accent-blue);
}

.filter-select {
    padding: 8px 12px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 0.85rem;
    font-family: var(--font);
}

.entry-count {
    font-size: 0.82rem;
    color: var(--text-muted);
}

.entry-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 600px;
    overflow-y: auto;
}

.entry-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 16px;
    cursor: pointer;
    transition: border-color 0.2s;
}

.entry-card:hover { border-color: var(--accent-blue); }
.entry-card.expanded { border-color: var(--accent-purple); }

.entry-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}

.entry-id {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--text-muted);
    flex-shrink: 0;
}

.entry-english {
    flex: 1;
    font-size: 0.85rem;
    color: var(--text-primary);
}

.entry-badge {
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    flex-shrink: 0;
}

.badge-exact { background: rgba(74,222,128,0.15); color: var(--accent-green); }
.badge-miss { background: rgba(248,113,113,0.15); color: var(--accent-red); }
.badge-error { background: rgba(251,191,36,0.15); color: var(--accent-amber); }

.entry-detail {
    display: none;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
    font-size: 0.82rem;
}

.entry-card.expanded .entry-detail { display: block; }

.detail-row {
    display: flex;
    margin-bottom: 6px;
    gap: 8px;
}

.detail-label {
    width: 100px;
    font-weight: 600;
    color: var(--text-secondary);
    flex-shrink: 0;
}

.detail-value {
    color: var(--text-primary);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    word-break: break-all;
}

.detail-value.match { color: var(--accent-green); }
.detail-value.diff { color: var(--accent-red); }

.plugin-group-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--accent-purple);
    margin: 16px 0 8px 0;
}
"""


# ---------------------------------------------------------------------------
# JavaScript — fully language-agnostic
# ---------------------------------------------------------------------------

_JS = """
(function() {
    // Use the first report for primary display
    const report = REPORTS[0];
    const overall = report.overall || {};
    const entries = report.entries || [];

    // ---------------------------------------------------------------
    // Metric cards — core metrics only (language-agnostic)
    // ---------------------------------------------------------------
    const cardsContainer = document.getElementById('metric-cards');

    // Core cards that always exist
    const cards = [
        { label: 'Entries', value: overall.evaluated || 0, color: '' },
        { label: 'Exact Match', value: pct(overall.exact_match_rate), color: 'green' },
        { label: 'Miss Rate', value: pct(overall.miss_rate), color: 'red' },
    ];

    // Conditionally add chrF++ and BLEU if present
    if (overall.corpus_chrf !== undefined) {
        cards.push({ label: 'Corpus chrF++', value: (overall.corpus_chrf || 0).toFixed(1), color: 'purple' });
    }
    if (overall.corpus_bleu !== undefined) {
        cards.push({ label: 'Corpus BLEU', value: (overall.corpus_bleu || 0).toFixed(1), color: 'blue' });
    }

    // Cost and latency
    if (overall.total_cost_usd) {
        cards.push({ label: 'Total Cost', value: '$' + (overall.total_cost_usd || 0).toFixed(4), color: '' });
    }
    if (overall.avg_latency_s) {
        cards.push({ label: 'Avg Latency', value: (overall.avg_latency_s || 0).toFixed(1) + 's', color: '' });
    }

    // Auto-detect plugin aggregate metrics and add as cards
    const pluginMetrics = overall.plugin_metrics || {};
    const pluginColors = ['amber', 'blue', 'purple', 'green'];
    let pci = 0;
    Object.entries(pluginMetrics).forEach(([pluginName, data]) => {
        if (typeof data === 'object' && !data.error) {
            Object.entries(data).forEach(([key, val]) => {
                if (typeof val === 'number') {
                    // Auto-format: rates (0-1 range) as percentages, others as decimals
                    const isRate = key.includes('rate') || key.includes('validity') || (val >= 0 && val <= 1 && key !== 'count');
                    const display = isRate ? pct(val) : val.toFixed(2);
                    const label = key.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
                    cards.push({ label: label, value: display, color: pluginColors[pci % pluginColors.length] });
                    pci++;
                }
            });
        }
    });

    cards.forEach(c => {
        const div = document.createElement('div');
        div.className = 'metric-card';
        div.innerHTML = `
            <div class="label">${c.label}</div>
            <div class="value ${c.color}">${c.value}</div>
        `;
        cardsContainer.appendChild(div);
    });

    // ---------------------------------------------------------------
    // Run comparison (if multiple reports)
    // ---------------------------------------------------------------
    if (REPORTS.length > 1) {
        document.getElementById('comparison-section').style.display = '';
        const wrap = document.getElementById('comparison-table-wrap');
        let html = '<table><thead><tr>';
        html += '<th>Run</th><th>Model</th><th>Exact</th>';
        html += '<th>chrF++</th><th>Cost</th></tr></thead><tbody>';

        REPORTS.forEach(r => {
            const o = r.overall || {};
            const c = r.config || {};
            html += `<tr>
                <td>${(r.run_id || '?').substring(0, 35)}</td>
                <td>${c.model || '?'}</td>
                <td class="num">${pct(o.exact_match_rate)}</td>
                <td class="num">${(o.corpus_chrf || 0).toFixed(1)}</td>
                <td class="num">$${(o.total_cost_usd || 0).toFixed(4)}</td>
            </tr>`;
        });

        html += '</tbody></table>';
        wrap.innerHTML = html;
    }

    // ---------------------------------------------------------------
    // Segment table
    // ---------------------------------------------------------------
    const segments = report.by_segment || {};
    const segWrap = document.getElementById('segment-table-wrap');
    let segHtml = '<table><thead><tr>';
    segHtml += '<th>Segment</th><th>Count</th><th>Exact</th>';
    segHtml += '<th>chrF++</th><th>Cost</th></tr></thead><tbody>';

    Object.entries(segments).sort().forEach(([name, s]) => {
        segHtml += `<tr>
            <td>${name}</td>
            <td class="num">${s.count}</td>
            <td class="num">${pct(s.exact_match_count / (s.count || 1))}</td>
            <td class="num">${(s.avg_chrf || 0).toFixed(1)}</td>
            <td class="num">$${(s.total_cost_usd || 0).toFixed(4)}</td>
        </tr>`;
    });

    segHtml += '</tbody></table>';
    segWrap.innerHTML = segHtml;

    // ---------------------------------------------------------------
    // Difficulty table
    // ---------------------------------------------------------------
    const diffs = report.by_difficulty || {};
    const diffWrap = document.getElementById('difficulty-table-wrap');
    let diffHtml = '<table><thead><tr>';
    diffHtml += '<th>Level</th><th>Count</th><th>Exact</th>';
    diffHtml += '<th>chrF++</th></tr></thead><tbody>';

    Object.entries(diffs).sort((a, b) => parseInt(a[0]) - parseInt(b[0])).forEach(([lvl, d]) => {
        diffHtml += `<tr>
            <td>L${lvl}</td>
            <td class="num">${d.count}</td>
            <td class="num">${pct(d.exact_match_count / (d.count || 1))}</td>
            <td class="num">${(d.avg_chrf || 0).toFixed(1)}</td>
        </tr>`;
    });

    diffHtml += '</tbody></table>';
    diffWrap.innerHTML = diffHtml;

    // ---------------------------------------------------------------
    // Plugin metric charts — dynamically rendered from plugin_metrics
    // ---------------------------------------------------------------
    if (Object.keys(pluginMetrics).length > 0) {
        document.getElementById('plugin-section').style.display = '';
        const container = document.getElementById('plugin-charts');
        const barColors = ['#60a5fa', '#a78bfa', '#4ade80', '#fbbf24', '#f87171', '#22d3ee'];

        Object.entries(pluginMetrics).forEach(([pluginName, data]) => {
            if (typeof data !== 'object' || data.error) return;

            // Add plugin group title
            container.innerHTML += `<div class="plugin-group-title">${pluginName}</div>`;

            // Render numeric values as bar charts
            const numericEntries = Object.entries(data).filter(([, v]) => typeof v === 'number');
            if (numericEntries.length === 0) return;

            const maxVal = Math.max(...numericEntries.map(([, v]) => v), 1);

            numericEntries.forEach(([key, val], i) => {
                const isRate = key.includes('rate') || key.includes('validity');
                const displayMax = isRate ? 1 : maxVal;
                const pctW = ((val / displayMax) * 100).toFixed(0);
                const displayVal = isRate ? pct(val) : val.toFixed(2);

                container.innerHTML += `
                    <div class="bar-row">
                        <div class="bar-label">${key}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${pctW}%; background:${barColors[i % barColors.length]}"></div>
                        </div>
                        <div class="bar-value">${displayVal}</div>
                    </div>`;
            });
        });
    }

    // ---------------------------------------------------------------
    // Entry explorer — language-agnostic
    // ---------------------------------------------------------------
    const searchInput = document.getElementById('search-input');
    const filterSegment = document.getElementById('filter-segment');
    const filterMatch = document.getElementById('filter-match');
    const entryList = document.getElementById('entry-list');
    const entryCountSpan = document.getElementById('entry-count');

    // Populate segment filter
    const segNames = [...new Set(entries.map(e => e.segment))].filter(Boolean).sort();
    segNames.forEach(s => {
        filterSegment.innerHTML += `<option value="${s}">${s}</option>`;
    });

    function renderEntries() {
        const query = searchInput.value.toLowerCase();
        const seg = filterSegment.value;
        const matchFilter = filterMatch.value;

        let filtered = entries.filter(e => {
            if (query && !e.english.toLowerCase().includes(query) &&
                !e.predicted.toLowerCase().includes(query) &&
                !e.expected.toLowerCase().includes(query)) return false;
            if (seg && e.segment !== seg) return false;
            if (matchFilter === 'exact' && !e.exact_match) return false;
            if (matchFilter === 'miss' && (e.exact_match || e.error)) return false;
            if (matchFilter === 'error' && !e.error) return false;
            return true;
        });

        entryCountSpan.textContent = `${filtered.length} / ${entries.length} entries`;

        // Render first 100 (performance)
        const toShow = filtered.slice(0, 100);
        let html = '';

        toShow.forEach(e => {
            let badge = '';
            if (e.error) badge = '<span class="entry-badge badge-error">Error</span>';
            else if (e.exact_match) badge = '<span class="entry-badge badge-exact">Exact</span>';
            else badge = '<span class="entry-badge badge-miss">Miss</span>';

            const tools = e.tool_call_count || 0;
            const predClass = e.exact_match ? 'match' : 'diff';

            // Build plugin metric rows dynamically
            let pluginRows = '';
            const pm = e.plugin_metrics || {};
            Object.entries(pm).forEach(([pName, pData]) => {
                if (typeof pData === 'object' && !pData.error) {
                    Object.entries(pData).forEach(([k, v]) => {
                        const label = k.replace(/_/g, ' ');
                        const display = typeof v === 'number' ? v.toFixed(4) : String(v);
                        pluginRows += `
                            <div class="detail-row">
                                <span class="detail-label">${escHtml(label)}</span>
                                <span class="detail-value">${escHtml(display)}</span>
                            </div>`;
                    });
                }
            });

            html += `
            <div class="entry-card" onclick="this.classList.toggle('expanded')">
                <div class="entry-header">
                    <span class="entry-id">#${e.id}</span>
                    <span class="entry-english">${escHtml(e.english)}</span>
                    ${badge}
                </div>
                <div class="entry-detail">
                    <div class="detail-row">
                        <span class="detail-label">Expected</span>
                        <span class="detail-value">${escHtml(e.expected)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Predicted</span>
                        <span class="detail-value ${predClass}">${escHtml(e.predicted)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">chrF++</span>
                        <span class="detail-value">${(e.chrf_score || 0).toFixed(1)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">BLEU</span>
                        <span class="detail-value">${(e.bleu_score || 0).toFixed(1)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Latency</span>
                        <span class="detail-value">${(e.latency_s || 0).toFixed(2)}s</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Cost</span>
                        <span class="detail-value">$${(e.cost_usd || 0).toFixed(6)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Tools</span>
                        <span class="detail-value">${tools} calls</span>
                    </div>
                    ${pluginRows}
                    ${e.error ? `<div class="detail-row"><span class="detail-label">Error</span><span class="detail-value diff">${escHtml(e.error)}</span></div>` : ''}
                </div>
            </div>`;
        });

        if (filtered.length > 100) {
            html += `<div class="entry-card" style="text-align:center;color:var(--text-muted)">
                Showing 100 of ${filtered.length} — refine your search
            </div>`;
        }

        entryList.innerHTML = html;
    }

    searchInput.addEventListener('input', renderEntries);
    filterSegment.addEventListener('change', renderEntries);
    filterMatch.addEventListener('change', renderEntries);
    renderEntries();

    // ---------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------
    function pct(v) {
        if (v === undefined || v === null) return '0%';
        return (v * 100).toFixed(1) + '%';
    }

    function escHtml(s) {
        if (!s) return '';
        return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }
})();
"""
