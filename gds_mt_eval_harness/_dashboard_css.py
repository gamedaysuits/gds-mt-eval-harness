"""
Dashboard CSS — GDS-branded dark theme.

Brand palette extracted from gamedaysuits.ca:
  - Primary: Royal blue (#3b4fa8) from the suit
  - Accent: Bright blue (#4466ff) from the tie
  - Dark navy: (#1a1f3a) background tones
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    /* GDS Brand */
    --gds-navy: #0d1021;
    --gds-navy-light: #151933;
    --gds-card: #1a1f3a;
    --gds-card-hover: #212752;
    --gds-royal: #3b4fa8;
    --gds-blue: #4466ff;
    --gds-blue-glow: rgba(68, 102, 255, 0.15);

    /* Semantic */
    --success: #34d399;
    --success-bg: rgba(52, 211, 153, 0.12);
    --danger: #f87171;
    --danger-bg: rgba(248, 113, 113, 0.12);
    --warning: #fbbf24;
    --warning-bg: rgba(251, 191, 36, 0.12);
    --info: #60a5fa;
    --info-bg: rgba(96, 165, 250, 0.12);
    --purple: #a78bfa;
    --purple-bg: rgba(167, 139, 250, 0.12);

    /* Text */
    --text-1: #eef0f6;
    --text-2: #9ca3bf;
    --text-3: #5c6380;

    /* Layout */
    --radius: 10px;
    --radius-sm: 6px;
    --border: rgba(255,255,255,0.06);
    --font: 'Inter', -apple-system, sans-serif;
    --mono: 'JetBrains Mono', 'Fira Code', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font);
    background: var(--gds-navy);
    color: var(--text-1);
    line-height: 1.6;
    min-height: 100vh;
}

/* ── Header ─────────────────────────────────────────── */
.header {
    background: linear-gradient(135deg, #0d1021 0%, #151933 50%, #1a1f3a 100%);
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(16px);
}

.header-logo {
    width: 42px;
    height: 42px;
    border-radius: 8px;
    flex-shrink: 0;
}

.header-text { flex: 1; }

.header-title {
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #7b8fff 0%, #4466ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-sub {
    font-size: 0.78rem;
    color: var(--text-3);
    margin-top: 1px;
}

/* ── Layout ─────────────────────────────────────────── */
.main { max-width: 1400px; margin: 0 auto; padding: 24px 32px; }

.section {
    margin-bottom: 24px;
    background: var(--gds-navy-light);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}

.section-head {
    padding: 16px 20px 12px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.section-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.section-body { padding: 20px; }

/* ── Run Tabs ───────────────────────────────────────── */
.run-tabs {
    display: flex;
    gap: 4px;
    padding: 12px 20px;
    background: var(--gds-navy);
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
}

.run-tab {
    padding: 8px 16px;
    border-radius: var(--radius-sm);
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-3);
    cursor: pointer;
    border: 1px solid transparent;
    background: transparent;
    white-space: nowrap;
    transition: all 0.2s;
    font-family: var(--font);
}

.run-tab:hover {
    color: var(--text-2);
    background: var(--gds-card);
}

.run-tab.active {
    color: var(--gds-blue);
    background: var(--gds-blue-glow);
    border-color: rgba(68, 102, 255, 0.3);
}

/* ── Metric Cards Grid ──────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
}

.metric-card {
    background: var(--gds-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    text-align: center;
    transition: border-color 0.2s;
}

.metric-card:hover { border-color: rgba(255,255,255,0.12); }

.metric-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-3);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    font-family: var(--mono);
    letter-spacing: -0.02em;
}

.c-green { color: var(--success); }
.c-red { color: var(--danger); }
.c-blue { color: var(--gds-blue); }
.c-purple { color: var(--purple); }
.c-amber { color: var(--warning); }
.c-default { color: var(--text-1); }

/* ── Comparison Table ───────────────────────────────── */
.cmp-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }

.cmp-table th {
    text-align: left;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-3);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
}

.cmp-table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text-1);
}

.cmp-table tr:hover td { background: rgba(255,255,255,0.02); }
.cmp-table .num { text-align: right; font-family: var(--mono); font-size: 0.8rem; }
.cmp-table .best { color: var(--success); font-weight: 600; }

/* ── Bars ────────────────────────────────────────────── */
.bar-group { display: flex; flex-direction: column; gap: 10px; }

.bar-row {
    display: grid;
    grid-template-columns: 140px 1fr 60px;
    align-items: center;
    gap: 12px;
}

.bar-label {
    font-size: 0.78rem;
    color: var(--text-2);
    text-align: right;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.bar-track {
    height: 22px;
    background: rgba(255,255,255,0.04);
    border-radius: 4px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
    min-width: 2px;
}

.bar-val {
    font-size: 0.78rem;
    font-family: var(--mono);
    color: var(--text-1);
    text-align: right;
}

/* ── Explorer ────────────────────────────────────────── */
.explorer-bar {
    display: flex;
    gap: 10px;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
    align-items: center;
}

.search-box {
    flex: 1;
    min-width: 200px;
    padding: 8px 12px;
    background: var(--gds-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-1);
    font-size: 0.82rem;
    font-family: var(--font);
    outline: none;
}

.search-box:focus { border-color: var(--gds-blue); }

.filter-sel {
    padding: 8px 12px;
    background: var(--gds-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-1);
    font-size: 0.82rem;
    font-family: var(--font);
}

.count-label { font-size: 0.75rem; color: var(--text-3); }

.entry-scroll {
    max-height: 700px;
    overflow-y: auto;
    padding: 12px 20px;
}

.entry {
    background: var(--gds-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.2s;
}

.entry:hover { border-color: rgba(68, 102, 255, 0.3); }
.entry.open { border-color: var(--gds-blue); }

.entry-top {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
}

.e-id {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--text-3);
    width: 36px;
    flex-shrink: 0;
}

.e-src {
    flex: 1;
    font-size: 0.82rem;
    color: var(--text-1);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.e-chrf {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--text-2);
    flex-shrink: 0;
}

.badge {
    font-size: 0.65rem;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    flex-shrink: 0;
}

.b-exact { background: var(--success-bg); color: var(--success); }
.b-miss { background: var(--danger-bg); color: var(--danger); }
.b-error { background: var(--warning-bg); color: var(--warning); }

.entry-detail {
    display: none;
    padding: 0 14px 14px;
    border-top: 1px solid var(--border);
    margin-top: 0;
}

.entry.open .entry-detail { display: block; padding-top: 12px; }

.d-grid {
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 6px 10px;
    font-size: 0.78rem;
}

.d-label { color: var(--text-3); font-weight: 600; }
.d-val { font-family: var(--mono); font-size: 0.76rem; color: var(--text-1); word-break: break-all; }
.d-match { color: var(--success); }
.d-diff { color: var(--danger); }

/* ── Multi-run comparison in entry detail ────────────── */
.run-compare-grid {
    display: grid;
    gap: 8px;
    margin-top: 8px;
}

.run-compare-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
}

.run-compare-label {
    font-size: 0.68rem;
    color: var(--gds-blue);
    font-weight: 600;
    margin-bottom: 6px;
}

/* ── Footer ──────────────────────────────────────────── */
.footer {
    text-align: center;
    padding: 24px;
    font-size: 0.72rem;
    color: var(--text-3);
    border-top: 1px solid var(--border);
    margin-top: 16px;
}

.footer a { color: var(--gds-blue); text-decoration: none; }

/* ── View Toggle ─────────────────────────────────────── */
.view-toggle {
    display: flex;
    gap: 4px;
    padding: 0 20px 12px;
}

.view-toggle-btn {
    padding: 7px 16px;
    border-radius: var(--radius-sm);
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-3);
    cursor: pointer;
    border: 1px solid var(--border);
    background: transparent;
    font-family: var(--font);
    transition: all 0.2s;
}

.view-toggle-btn:hover { color: var(--text-2); background: var(--gds-card); }

.view-toggle-btn.active {
    color: var(--gds-blue);
    background: var(--gds-blue-glow);
    border-color: rgba(68, 102, 255, 0.3);
}

/* ── Side-by-Side Table ──────────────────────────────── */
.sbs-table { font-size: 0.78rem; }
.sbs-table th { position: sticky; top: 0; background: var(--gds-navy-light); z-index: 2; }
.sbs-src { max-width: 200px; font-size: 0.78rem; color: var(--text-2); }
.sbs-exp { max-width: 180px; font-family: var(--mono); font-size: 0.74rem; color: var(--text-2); }

.sbs-cell { vertical-align: top; padding: 8px 10px !important; }
.sbs-exact { background: rgba(52, 211, 153, 0.06); }
.sbs-miss { background: rgba(248, 113, 113, 0.06); }

.sbs-pred {
    font-family: var(--mono);
    font-size: 0.74rem;
    word-break: break-all;
    margin-bottom: 3px;
}

.sbs-exact .sbs-pred { color: var(--success); }
.sbs-miss .sbs-pred { color: var(--danger); }

.sbs-meta {
    font-size: 0.65rem;
    color: var(--text-3);
}

.sbs-wrap {
    max-height: 700px;
    overflow: auto;
}

/* ── Chart Containers ────────────────────────────────── */
.chart-wrap {
    display: flex;
    justify-content: center;
    padding: 8px 0;
}

/* ── License Bar ─────────────────────────────────────── */
.license-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    padding: 8px 20px;
    font-size: 0.7rem;
    color: var(--text-3);
    border-top: 1px solid var(--border);
    flex-wrap: wrap;
}

.license-bar span { white-space: nowrap; }
"""
