"""
Dashboard JavaScript v2 — complete rendering logic.

Sections rendered:
  1. Run tabs (clickable switcher)
  2. Metric cards (active run) + cost-effectiveness metrics
  3. Run comparison table (multi-run, best-value highlighting)
  4. SVG grouped bar chart (exact match + chrF++ per run)
  5. Segment breakdown bars (active run)
  6. Segment × Run matrix table
  7. chrF++ distribution histogram (SVG, active run)
  8. Side-by-Side comparison view (all entries, all runs in columns)
  9. Entry explorer (single-run drill-down with search/filter)
"""

JS = r"""
(function() {
    const R = window.__REPORTS;
    if (!R || !R.length) return;
    let activeIdx = 0;
    let viewMode = 'explorer'; // 'explorer' | 'sidebyside'

    // ── Helpers ──────────────────────────────────────
    const pct = v => v == null ? '—' : (v * 100).toFixed(1) + '%';
    const f1 = v => v == null ? '—' : Number(v).toFixed(1);
    const f4 = v => v == null ? '—' : '$' + Number(v).toFixed(4);
    const esc = s => s ? s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : '';
    const $ = id => document.getElementById(id);
    const RUN_COLORS = ['#4466ff','#34d399','#a78bfa','#fbbf24','#f87171','#22d3ee','#fb923c','#e879f9'];
    function runLabel(r, i) {
        const c = r.config || {};
        return (c.run_name || c.model || r.run_id || 'Run '+(i+1)).substring(0, 35);
    }

    // ── 1. Run Tabs ─────────────────────────────────
    function buildTabs() {
        const bar = $('run-tabs');
        bar.innerHTML = '';
        R.forEach((r, i) => {
            const btn = document.createElement('button');
            btn.className = 'run-tab' + (i === activeIdx ? ' active' : '');
            btn.textContent = runLabel(r, i);
            btn.onclick = () => { activeIdx = i; render(); };
            bar.appendChild(btn);
        });
    }

    // ── 2. Metric Cards ─────────────────────────────
    function buildCards() {
        const o = R[activeIdx].overall || {};
        const cards = [
            ['Entries', o.evaluated || 0, 'default'],
            ['Exact Match', pct(o.exact_match_rate), o.exact_match_rate >= 0.5 ? 'green' : 'red'],
            ['Miss Rate', pct(o.miss_rate), 'red'],
        ];
        if (o.corpus_chrf != null) cards.push(['chrF++', f1(o.corpus_chrf), 'purple']);
        if (o.corpus_bleu != null) cards.push(['BLEU', f1(o.corpus_bleu), 'blue']);
        if (o.total_cost_usd != null) cards.push(['Total Cost', f4(o.total_cost_usd), 'default']);
        if (o.avg_latency_s != null) cards.push(['Avg Latency', f1(o.avg_latency_s) + 's', 'default']);

        // Cost-effectiveness: cost per exact match
        if (o.total_cost_usd && o.exact_match_count) {
            const cpe = (o.total_cost_usd / o.exact_match_count);
            cards.push(['Cost/Match', '$' + cpe.toFixed(4), 'amber']);
        }

        // Plugin aggregate metrics
        const pm = o.plugin_metrics || {};
        const pCols = ['amber','blue','purple','green'];
        let pi = 0;
        Object.entries(pm).forEach(([, data]) => {
            if (typeof data !== 'object' || data.error) return;
            Object.entries(data).forEach(([k, v]) => {
                if (typeof v !== 'number') return;
                const isR = k.includes('rate') || k.includes('validity');
                cards.push([k.replace(/_/g,' '), isR ? pct(v) : f1(v), pCols[pi++ % 4]]);
            });
        });

        $('metric-cards').innerHTML = cards.map(([l,v,c]) =>
            `<div class="metric-card"><div class="metric-label">${l}</div>` +
            `<div class="metric-value c-${c}">${v}</div></div>`
        ).join('');
    }

    // ── 3. Run Comparison Table ──────────────────────
    function buildCompare() {
        const sec = $('compare-section');
        if (R.length < 2) { sec.style.display = 'none'; return; }
        sec.style.display = '';
        const rates = R.map(r => r.overall?.exact_match_rate || 0);
        const chrfs = R.map(r => r.overall?.corpus_chrf || 0);
        const costs = R.map(r => r.overall?.total_cost_usd || 999);
        const bestR = Math.max(...rates), bestC = Math.max(...chrfs), bestCost = Math.min(...costs);

        let h = '<table class="cmp-table"><thead><tr>';
        h += '<th>Run</th><th>Model</th><th>Prompt</th><th class="num">N</th>';
        h += '<th class="num">Exact</th><th class="num">chrF++</th><th class="num">BLEU</th>';
        h += '<th class="num">Cost</th><th class="num">Latency</th><th class="num">$/Match</th>';
        h += '</tr></thead><tbody>';
        R.forEach((r, i) => {
            const o = r.overall || {}, c = r.config || {};
            const rc = o.exact_match_rate === bestR ? ' best' : '';
            const cc = o.corpus_chrf === bestC ? ' best' : '';
            const costc = o.total_cost_usd === bestCost ? ' best' : '';
            const bg = i === activeIdx ? ' style="background:var(--gds-blue-glow)"' : '';
            const cpm = o.exact_match_count ? '$'+(o.total_cost_usd / o.exact_match_count).toFixed(4) : '—';
            h += `<tr${bg}><td>${esc(runLabel(r,i))}</td><td>${esc(c.model||'?')}</td>`;
            h += `<td>${esc(c.prompt||'?')}</td><td class="num">${o.evaluated||0}</td>`;
            h += `<td class="num${rc}">${pct(o.exact_match_rate)}</td>`;
            h += `<td class="num${cc}">${f1(o.corpus_chrf)}</td>`;
            h += `<td class="num">${f1(o.corpus_bleu)}</td>`;
            h += `<td class="num${costc}">${f4(o.total_cost_usd)}</td>`;
            h += `<td class="num">${f1(o.avg_latency_s)}s</td>`;
            h += `<td class="num">${cpm}</td></tr>`;
        });
        h += '</tbody></table>';
        $('compare-table').innerHTML = h;
    }

    // ── 4. SVG Grouped Bar Chart ────────────────────
    function buildBarChart() {
        const sec = $('barchart-section');
        if (R.length < 2) { sec.style.display = 'none'; return; }
        sec.style.display = '';
        const W = 600, H = 200, PAD = 50, PADT = 20;
        const metrics = [
            { key: 'exact_match_rate', label: 'Exact %', scale: 100 },
            { key: 'corpus_chrf', label: 'chrF++', scale: 1 },
        ];
        const groupW = (W - PAD) / metrics.length;
        const barW = Math.min(30, (groupW - 20) / R.length);

        let svg = `<svg viewBox="0 0 ${W} ${H + 30}" style="width:100%;max-width:${W}px">`;
        // Axis line
        svg += `<line x1="${PAD}" y1="${H}" x2="${W}" y2="${H}" stroke="rgba(255,255,255,0.1)"/>`;
        // Y axis labels
        [0,25,50,75,100].forEach(v => {
            const y = H - (v/100)*(H-PADT);
            svg += `<text x="${PAD-5}" y="${y+4}" fill="rgba(255,255,255,0.3)" font-size="10" text-anchor="end">${v}</text>`;
            svg += `<line x1="${PAD}" y1="${y}" x2="${W}" y2="${y}" stroke="rgba(255,255,255,0.04)"/>`;
        });

        metrics.forEach((m, mi) => {
            const gx = PAD + mi * groupW + 10;
            // Group label
            svg += `<text x="${gx + (R.length*barW)/2}" y="${H+18}" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">${m.label}</text>`;
            R.forEach((r, ri) => {
                const val = (r.overall || {})[m.key] || 0;
                const normed = (val * m.scale);
                const bh = (normed / 100) * (H - PADT);
                const bx = gx + ri * (barW + 2);
                const by = H - bh;
                svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" fill="${RUN_COLORS[ri % RUN_COLORS.length]}" rx="2" opacity="0.85"/>`;
                svg += `<text x="${bx+barW/2}" y="${by-4}" fill="${RUN_COLORS[ri % RUN_COLORS.length]}" font-size="9" text-anchor="middle">${normed.toFixed(1)}</text>`;
            });
        });

        // Legend
        R.forEach((r, i) => {
            const lx = PAD + i * 120;
            svg += `<rect x="${lx}" y="${H+24}" width="10" height="10" fill="${RUN_COLORS[i % RUN_COLORS.length]}" rx="2"/>`;
            svg += `<text x="${lx+14}" y="${H+33}" fill="rgba(255,255,255,0.6)" font-size="10">${esc(runLabel(r,i).substring(0,18))}</text>`;
        });

        svg += '</svg>';
        $('barchart').innerHTML = svg;
    }

    // ── 5. Segment Bars ─────────────────────────────
    function buildSegments() {
        const segs = R[activeIdx].by_segment || {};
        const keys = Object.keys(segs).sort();
        if (!keys.length) { $('segment-section').style.display = 'none'; return; }
        $('segment-section').style.display = '';
        let h = '';
        keys.forEach((name, i) => {
            const s = segs[name], rate = s.exact_match_count / (s.count || 1);
            const color = RUN_COLORS[i % RUN_COLORS.length];
            h += `<div class="bar-row"><div class="bar-label">${esc(name)} <span style="color:var(--text-3)">(${s.count})</span></div>`;
            h += `<div class="bar-track"><div class="bar-fill" style="width:${(rate*100).toFixed(0)}%;background:${color}"></div></div>`;
            h += `<div class="bar-val">${pct(rate)}</div></div>`;
            h += `<div class="bar-row" style="margin-top:-4px;margin-bottom:4px">`;
            h += `<div class="bar-label" style="font-size:0.7rem;color:var(--text-3)">chrF++</div>`;
            h += `<div class="bar-track" style="height:10px"><div class="bar-fill" style="width:${(s.avg_chrf||0).toFixed(0)}%;background:${color};opacity:0.4"></div></div>`;
            h += `<div class="bar-val" style="font-size:0.72rem">${f1(s.avg_chrf)}</div></div>`;
        });
        $('segment-bars').innerHTML = h;
    }

    // ── 6. Segment × Run Matrix ─────────────────────
    function buildSegmentCompare() {
        const sec = $('seg-compare-section');
        if (R.length < 2) { sec.style.display = 'none'; return; }
        sec.style.display = '';
        const allSegs = new Set();
        R.forEach(r => Object.keys(r.by_segment || {}).forEach(s => allSegs.add(s)));
        const segNames = [...allSegs].sort();
        let h = '<table class="cmp-table"><thead><tr><th>Segment</th>';
        R.forEach((r, i) => { h += `<th class="num">${esc(runLabel(r,i).substring(0,20))}</th>`; });
        h += '</tr></thead><tbody>';
        segNames.forEach(name => {
            h += `<tr><td>${esc(name)}</td>`;
            const vals = R.map(r => { const s = (r.by_segment||{})[name]; return s ? s.exact_match_count/(s.count||1) : null; });
            const best = Math.max(...vals.filter(v=>v!==null));
            vals.forEach(v => { h += `<td class="num${v===best?' best':''}">${v!=null?pct(v):'—'}</td>`; });
            h += '</tr>';
        });
        h += '</tbody></table>';
        $('seg-compare-table').innerHTML = h;
    }

    // ── 7. chrF++ Histogram ─────────────────────────
    function buildHistogram() {
        const entries = R[activeIdx].entries || [];
        if (!entries.length) { $('histogram-section').style.display = 'none'; return; }
        $('histogram-section').style.display = '';
        const scores = entries.map(e => e.chrf_score || 0);
        const bins = new Array(10).fill(0); // 0-10, 10-20, ..., 90-100
        scores.forEach(s => { const b = Math.min(9, Math.floor(s / 10)); bins[b]++; });
        const maxBin = Math.max(...bins, 1);
        const W = 500, H = 150, PAD = 35, PADB = 25;
        const bw = (W - PAD) / 10 - 2;
        const color = RUN_COLORS[activeIdx % RUN_COLORS.length];

        let svg = `<svg viewBox="0 0 ${W} ${H + PADB}" style="width:100%;max-width:${W}px">`;
        svg += `<line x1="${PAD}" y1="${H}" x2="${W}" y2="${H}" stroke="rgba(255,255,255,0.1)"/>`;
        bins.forEach((count, i) => {
            const bx = PAD + i * ((W-PAD)/10) + 1;
            const bh = (count / maxBin) * (H - 10);
            const by = H - bh;
            svg += `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" fill="${color}" rx="2" opacity="0.75"/>`;
            if (count > 0) svg += `<text x="${bx+bw/2}" y="${by-3}" fill="rgba(255,255,255,0.6)" font-size="9" text-anchor="middle">${count}</text>`;
            svg += `<text x="${bx+bw/2}" y="${H+14}" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">${i*10}</text>`;
        });
        svg += `<text x="${W/2+PAD/2}" y="${H+PADB}" fill="rgba(255,255,255,0.3)" font-size="10" text-anchor="middle">chrF++ Score Range</text>`;
        svg += '</svg>';
        $('histogram').innerHTML = svg;
    }

    // ── 8. Side-by-Side View ────────────────────────
    function buildSideBySide() {
        const sec = $('sbs-section');
        if (viewMode !== 'sidebyside') { sec.style.display = 'none'; return; }
        sec.style.display = '';
        // Collect all unique entry IDs across all runs
        const idMap = new Map();
        R.forEach((r, ri) => {
            (r.entries || []).forEach(e => {
                if (!idMap.has(e.id)) idMap.set(e.id, { id: e.id, english: e.english, expected: e.expected, segment: e.segment, runs: {} });
                idMap.get(e.id).runs[ri] = e;
            });
        });
        let allEntries = [...idMap.values()].sort((a,b) => a.id - b.id);

        // Apply filters
        const q = ($('sbs-search').value || '').toLowerCase();
        const sf = $('sbs-filter-seg').value;
        const mf = $('sbs-filter-match').value;
        if (q) allEntries = allEntries.filter(e => e.english?.toLowerCase().includes(q) || e.expected?.toLowerCase().includes(q));
        if (sf) allEntries = allEntries.filter(e => e.segment === sf);
        if (mf === 'disagree') {
            allEntries = allEntries.filter(e => {
                const matches = Object.values(e.runs).map(r => r.exact_match);
                return matches.some(m => m) && matches.some(m => !m);
            });
        } else if (mf === 'all_miss') {
            allEntries = allEntries.filter(e => Object.values(e.runs).every(r => !r.exact_match));
        } else if (mf === 'all_exact') {
            allEntries = allEntries.filter(e => Object.values(e.runs).every(r => r.exact_match));
        }

        $('sbs-count').textContent = `${allEntries.length} entries`;

        // Populate segment filter
        const segSel = $('sbs-filter-seg');
        const allSegs = [...new Set([...idMap.values()].map(e => e.segment))].filter(Boolean).sort();
        const curSeg = segSel.value;
        segSel.innerHTML = '<option value="">All segments</option>' + allSegs.map(s => `<option value="${s}"${s===curSeg?' selected':''}>${s}</option>`).join('');

        const show = allEntries.slice(0, 200);
        let h = '<table class="cmp-table sbs-table"><thead><tr>';
        h += '<th style="width:30px">ID</th><th>Source</th><th>Expected</th>';
        R.forEach((r, i) => {
            h += `<th style="min-width:150px"><span style="color:${RUN_COLORS[i%RUN_COLORS.length]}">${esc(runLabel(r,i).substring(0,20))}</span></th>`;
        });
        h += '</tr></thead><tbody>';

        show.forEach(e => {
            h += `<tr><td class="num">${e.id}</td>`;
            h += `<td class="sbs-src">${esc(e.english)}</td>`;
            h += `<td class="sbs-exp">${esc(e.expected)}</td>`;
            R.forEach((r, ri) => {
                const entry = e.runs[ri];
                if (!entry) { h += '<td class="sbs-cell">—</td>'; return; }
                const cls = entry.exact_match ? 'sbs-exact' : 'sbs-miss';
                h += `<td class="sbs-cell ${cls}">`;
                h += `<div class="sbs-pred">${esc(entry.predicted)}</div>`;
                h += `<div class="sbs-meta">${f1(entry.chrf_score)} chrF · ${f4(entry.cost_usd)}</div>`;
                h += '</td>';
            });
            h += '</tr>';
        });
        h += '</tbody></table>';
        if (allEntries.length > 200) h += `<div style="text-align:center;padding:12px;color:var(--text-3);font-size:0.8rem">Showing 200 of ${allEntries.length}</div>`;
        $('sbs-table-wrap').innerHTML = h;
    }

    // ── 9. Entry Explorer ───────────────────────────
    function buildExplorer() {
        const sec = $('explorer-section');
        if (viewMode !== 'explorer') { sec.style.display = 'none'; return; }
        sec.style.display = '';
        const entries = R[activeIdx].entries || [];
        const segSel = $('filter-seg');
        const segNames = [...new Set(entries.map(e => e.segment))].filter(Boolean).sort();
        const cv = segSel.value;
        segSel.innerHTML = '<option value="">All segments</option>' + segNames.map(s => `<option value="${s}"${s===cv?' selected':''}>${s}</option>`).join('');
        renderEntries();
    }

    function renderEntries() {
        const entries = R[activeIdx].entries || [];
        const q = ($('search-box').value || '').toLowerCase();
        const seg = $('filter-seg').value;
        const mf = $('filter-match').value;
        let filtered = entries.filter(e => {
            if (q && !e.english?.toLowerCase().includes(q) && !e.predicted?.toLowerCase().includes(q) && !e.expected?.toLowerCase().includes(q)) return false;
            if (seg && e.segment !== seg) return false;
            if (mf === 'exact' && !e.exact_match) return false;
            if (mf === 'miss' && (e.exact_match || e.error)) return false;
            if (mf === 'error' && !e.error) return false;
            return true;
        });
        $('entry-count').textContent = `${filtered.length} / ${entries.length}`;
        const show = filtered.slice(0, 150);
        let h = '';
        show.forEach(e => {
            const badge = e.error ? '<span class="badge b-error">ERR</span>' : e.exact_match ? '<span class="badge b-exact">EXACT</span>' : '<span class="badge b-miss">MISS</span>';
            const pc = e.exact_match ? 'd-match' : 'd-diff';
            // Cross-run comparison cards
            let multiH = '';
            if (R.length > 1) {
                multiH = '<div class="run-compare-grid">';
                R.forEach((rr, ri) => {
                    if (ri === activeIdx) return;
                    const other = (rr.entries||[]).find(oe => oe.id === e.id);
                    if (!other) return;
                    const oc = other.exact_match ? 'd-match' : 'd-diff';
                    const ob = other.exact_match ? '<span class="badge b-exact" style="font-size:0.58rem">EXACT</span>' : '<span class="badge b-miss" style="font-size:0.58rem">MISS</span>';
                    multiH += `<div class="run-compare-card"><div class="run-compare-label">${esc(runLabel(rr,ri))} ${ob}</div>`;
                    multiH += `<div class="d-grid"><span class="d-label">Predicted</span><span class="d-val ${oc}">${esc(other.predicted)}</span>`;
                    multiH += `<span class="d-label">chrF++</span><span class="d-val">${f1(other.chrf_score)}</span></div></div>`;
                });
                multiH += '</div>';
            }
            let plugH = '';
            Object.entries(e.plugin_metrics || {}).forEach(([, pData]) => {
                if (typeof pData !== 'object' || pData.error) return;
                Object.entries(pData).forEach(([k, v]) => {
                    plugH += `<span class="d-label">${esc(k.replace(/_/g,' '))}</span><span class="d-val">${typeof v==='number'?f1(v):esc(String(v))}</span>`;
                });
            });
            h += `<div class="entry" onclick="this.classList.toggle('open')"><div class="entry-top">`;
            h += `<span class="e-id">#${e.id}</span><span class="e-src">${esc(e.english)}</span>`;
            h += `<span class="e-chrf">${f1(e.chrf_score)}</span>${badge}</div>`;
            h += `<div class="entry-detail"><div class="d-grid">`;
            h += `<span class="d-label">Expected</span><span class="d-val">${esc(e.expected)}</span>`;
            h += `<span class="d-label">Predicted</span><span class="d-val ${pc}">${esc(e.predicted)}</span>`;
            h += `<span class="d-label">chrF++</span><span class="d-val">${f1(e.chrf_score)}</span>`;
            h += `<span class="d-label">Latency</span><span class="d-val">${f1(e.latency_s)}s</span>`;
            h += `<span class="d-label">Cost</span><span class="d-val">${f4(e.cost_usd)}</span>`;
            h += plugH;
            if (e.error) h += `<span class="d-label">Error</span><span class="d-val d-diff">${esc(e.error)}</span>`;
            h += `</div>${multiH}</div></div>`;
        });
        if (filtered.length > 150) h += `<div style="text-align:center;padding:12px;color:var(--text-3);font-size:0.8rem">Showing 150/${filtered.length}</div>`;
        $('entry-list').innerHTML = h;
    }

    // ── View Toggle ─────────────────────────────────
    function bindViewToggle() {
        document.querySelectorAll('.view-toggle-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                viewMode = btn.dataset.view;
                document.querySelectorAll('.view-toggle-btn').forEach(b => b.classList.toggle('active', b.dataset.view === viewMode));
                render();
            });
        });
    }

    // ── Render All ───────────────────────────────────
    function render() {
        buildTabs();
        buildCards();
        buildCompare();
        buildBarChart();
        buildSegments();
        buildSegmentCompare();
        buildHistogram();
        buildSideBySide();
        buildExplorer();
    }

    // ── Bind Events ─────────────────────────────────
    $('search-box').addEventListener('input', renderEntries);
    $('filter-seg').addEventListener('change', renderEntries);
    $('filter-match').addEventListener('change', renderEntries);
    $('sbs-search')?.addEventListener('input', buildSideBySide);
    $('sbs-filter-seg')?.addEventListener('change', buildSideBySide);
    $('sbs-filter-match')?.addEventListener('change', buildSideBySide);
    bindViewToggle();
    render();
})();
"""
