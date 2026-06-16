/**
 * Champollion Competitive Landscape — Interactive Application (v2)
 * 
 * Handles: filtering, sorting, card rendering, comparison table,
 * radar chart (canvas-drawn, no dependencies), custom tooltips,
 * scroll-reveal animations, mobile nav toggle, column highlighting.
 */

(function() {
  'use strict';

  // ── State ──────────────────────────────────────────────────────
  let activeCategory = 'all';
  let activeCapabilities = new Set();
  let sortMode = 'relevance';
  // Tracks which view (cards vs table) is visible in the landscape section
  let activeView = 'cards';

  // ── DOM References ─────────────────────────────────────────────
  const gridEl = document.getElementById('project-grid');
  const noResultsEl = document.getElementById('no-results');
  const tableHeaderEl = document.getElementById('table-header');
  const tableBodyEl = document.getElementById('table-body');
  const radarCanvas = document.getElementById('radar-canvas');
  const radarCtx = radarCanvas.getContext('2d');
  const radarSelectA = document.getElementById('radar-select-a');
  const radarSelectB = document.getElementById('radar-select-b');
  const radarLegendEl = document.getElementById('radar-legend');
  const sortSelect = document.getElementById('sort-select');
  const tooltipEl = document.getElementById('custom-tooltip');
  const navToggle = document.getElementById('nav-toggle');
  const navLinks = document.getElementById('nav-links');
  // The table-view wrapper lives alongside the card grid inside .grid-section
  const tableViewEl = document.getElementById('table-view');

  // ── Helpers ────────────────────────────────────────────────────

  /**
   * Convert a capability value to a numeric score for the radar chart.
   * true = 1, 'partial' = 0.5, false = 0
   */
  function capScore(val) {
    if (val === true) return 1;
    if (val === 'partial') return 0.5;
    return 0;
  }

  /**
   * Get the total capability count for a project (used for sorting).
   */
  function totalCaps(project) {
    return DIMENSIONS.reduce((sum, d) => sum + capScore(project.capabilities[d.key]), 0);
  }

  /**
   * Escape HTML entities in a string for safe insertion into attributes.
   * We use this for aria-label and similar — NOT for tooltip content
   * (which uses textContent instead of innerHTML).
   */
  function escapeAttr(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  /**
   * Check if a project matches the current filters.
   */
  function matchesFilters(project) {
    if (activeCategory !== 'all' && project.category !== activeCategory) {
      return false;
    }
    for (const cap of activeCapabilities) {
      const val = project.capabilities[cap];
      if (val !== true && val !== 'partial') {
        return false;
      }
    }
    return true;
  }

  /**
   * Sort projects based on the current sort mode.
   */
  function sortProjects(projects) {
    const sorted = [...projects];
    switch (sortMode) {
      case 'relevance':
        sorted.sort((a, b) => b.relevance - a.relevance);
        break;
      case 'name':
        sorted.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'capabilities':
        sorted.sort((a, b) => totalCaps(b) - totalCaps(a));
        break;
      case 'category':
        sorted.sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
        break;
    }
    return sorted;
  }

  // ── Custom Tooltip System ─────────────────────────────────────
  //
  // Uses a single positioned <div> instead of native title="" attributes.
  // Why: native tooltips break on em-dashes (—), ® symbols, and quotes
  // inside HTML attribute values. They're also ugly and have a ~500ms delay.

  function showTooltip(targetEl, text) {
    tooltipEl.textContent = text;
    tooltipEl.classList.add('visible');
    tooltipEl.setAttribute('aria-hidden', 'false');

    // Position near the target element
    const rect = targetEl.getBoundingClientRect();
    const tipWidth = 320; // max-width from CSS

    // Default: show below the element
    let top = rect.bottom + 8;
    let left = rect.left + rect.width / 2 - tipWidth / 2;

    // Keep within viewport horizontally
    left = Math.max(8, Math.min(left, window.innerWidth - tipWidth - 8));

    // If it would go below viewport, show above
    if (top + 100 > window.innerHeight) {
      top = rect.top - 8;
      tooltipEl.style.transform = 'translateY(-100%)';
    } else {
      tooltipEl.style.transform = 'translateY(0)';
    }

    tooltipEl.style.top = top + 'px';
    tooltipEl.style.left = left + 'px';
  }

  function hideTooltip() {
    tooltipEl.classList.remove('visible');
    tooltipEl.setAttribute('aria-hidden', 'true');
  }

  /**
   * Attach tooltip behavior to all elements with data-tooltip attribute.
   * Called after every re-render.
   */
  function attachTooltips(container) {
    container.querySelectorAll('[data-tooltip]').forEach(el => {
      el.addEventListener('mouseenter', () => {
        const text = el.getAttribute('data-tooltip');
        if (text) showTooltip(el, text);
      });
      el.addEventListener('mouseleave', hideTooltip);
      el.addEventListener('focus', () => {
        const text = el.getAttribute('data-tooltip');
        if (text) showTooltip(el, text);
      });
      el.addEventListener('blur', hideTooltip);
    });
  }

  // ── Card Grid ──────────────────────────────────────────────────

  function renderGrid() {
    const filtered = PROJECTS.filter(matchesFilters);
    const sorted = sortProjects(filtered);

    if (sorted.length === 0) {
      gridEl.innerHTML = '';
      noResultsEl.style.display = 'block';
      return;
    }

    noResultsEl.style.display = 'none';

    gridEl.innerHTML = sorted.map(p => {
      const isChampollion = p.id === 'champollion';

      // Build capability badges with data-tooltip (not title)
      const capBadges = DIMENSIONS.map(d => {
        const val = p.capabilities[d.key];
        const cls = val === true ? '' : val === 'partial' ? '' : 'absent';
        const icon = val === true ? '✓' : val === 'partial' ? '~' : '✗';
        // data-tooltip stores the dimension info text — rendered by JS, not by HTML attribute
        return `<span class="cap-badge ${cls}" data-tooltip="${escapeAttr(d.info)}" tabindex="0">${icon} ${d.short}</span>`;
      }).join('');

      return `
        <div class="project-card ${isChampollion ? 'champollion' : ''}" data-id="${p.id}" tabindex="0" role="button" aria-expanded="false">
          <div class="card-header">
            <span class="card-name">${p.name}</span>
            <span class="card-category cat-${p.category}">${formatCategory(p.category)}</span>
          </div>
          <div class="card-org">${p.org}</div>
          <div class="card-desc">${p.desc}</div>
          <div class="card-caps">${capBadges}</div>
          <div class="card-detail">
            <div class="card-detail-inner">
              <p>${p.detail}</p>
              ${p.url ? `<p><a href="${p.url}" target="_blank" rel="noopener">${p.url}</a></p>` : ''}
            </div>
          </div>
          <div class="card-expand-hint">click to expand</div>
        </div>
      `;
    }).join('');

    // Attach click AND keyboard handlers for expanding cards
    gridEl.querySelectorAll('.project-card').forEach(card => {
      function toggleCard(e) {
        // Don't toggle if clicking a link or tooltip-bearing element
        if (e.target.closest('a') || e.target.closest('[data-tooltip]')) return;

        const isExpanded = card.classList.toggle('expanded');
        card.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
      }

      card.addEventListener('click', toggleCard);
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleCard(e);
        }
      });
    });

    // Attach custom tooltips to badge elements
    attachTooltips(gridEl);
  }

  function formatCategory(cat) {
    const map = {
      'benchmark': 'Benchmark',
      'eval-tool': 'Eval Tool',
      'model': 'Model',
      'community': 'Community',
      'commercial': 'Commercial',
      'platform': 'Platform',
      'framework': 'Framework',
    };
    return map[cat] || cat;
  }

  // ── Comparison Table (Transposed: features=rows, projects=columns) ──

  function renderTable() {
    const filtered = PROJECTS.filter(matchesFilters);
    const sorted = sortProjects(filtered);

    // Header row: "Feature" corner cell + one column per project
    // Each header gets a data-col-index for column highlighting
    tableHeaderEl.innerHTML = `
      <th>Feature</th>
      ${sorted.map((p, colIdx) => {
        const isChampollion = p.id === 'champollion';
        return `<th class="${isChampollion ? 'col-champollion' : ''}" 
                    data-tooltip="${escapeAttr(p.desc)}" 
                    data-col-index="${colIdx + 1}"
                    tabindex="0">${p.name}</th>`;
      }).join('')}
    `;

    // One row per dimension, cells are each project's score
    tableBodyEl.innerHTML = DIMENSIONS.map(d => {
      const cells = sorted.map((p, colIdx) => {
        const val = p.capabilities[d.key];
        const isChampollion = p.id === 'champollion';
        const colClass = isChampollion ? ' col-champollion' : '';
        if (val === true) return `<td class="cell-yes${colClass}" data-col-index="${colIdx + 1}">✅</td>`;
        if (val === 'partial') return `<td class="cell-partial${colClass}" data-col-index="${colIdx + 1}">⚠️</td>`;
        return `<td class="cell-no${colClass}" data-col-index="${colIdx + 1}">—</td>`;
      }).join('');

      // data-tooltip on the ⓘ icon — custom tooltip, not title attribute
      return `<tr>
        <td><span class="dim-label">${d.label}</span><span class="dim-info" data-tooltip="${escapeAttr(d.info)}" tabindex="0">ⓘ</span></td>
        ${cells}
      </tr>`;
    }).join('');

    // Attach tooltips to table headers and info icons
    attachTooltips(document.getElementById('comparison-table'));

    // Column highlighting on header hover
    const table = document.getElementById('comparison-table');
    table.querySelectorAll('th[data-col-index]').forEach(th => {
      th.addEventListener('mouseenter', () => {
        const colIdx = th.getAttribute('data-col-index');
        table.querySelectorAll(`[data-col-index="${colIdx}"]`).forEach(cell => {
          cell.classList.add('col-highlight');
        });
      });
      th.addEventListener('mouseleave', () => {
        const colIdx = th.getAttribute('data-col-index');
        table.querySelectorAll(`[data-col-index="${colIdx}"]`).forEach(cell => {
          cell.classList.remove('col-highlight');
        });
      });
    });
  }

  // ── Radar Chart ────────────────────────────────────────────────

  function populateRadarSelects() {
    const options = PROJECTS.map(p =>
      `<option value="${p.id}" ${p.id === 'champollion' ? 'selected' : ''}>${p.name}</option>`
    ).join('');

    radarSelectA.innerHTML = options;
    radarSelectB.innerHTML = PROJECTS.map(p =>
      `<option value="${p.id}" ${p.id === 'wmt' ? 'selected' : ''}>${p.name}</option>`
    ).join('');
  }

  function drawRadar() {
    const projectA = PROJECTS.find(p => p.id === radarSelectA.value);
    const projectB = PROJECTS.find(p => p.id === radarSelectB.value);
    if (!projectA || !projectB) return;

    // Handle high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    const displaySize = Math.min(500, window.innerWidth - 40);
    radarCanvas.style.width = displaySize + 'px';
    radarCanvas.style.height = displaySize + 'px';
    radarCanvas.width = displaySize * dpr;
    radarCanvas.height = displaySize * dpr;
    radarCtx.scale(dpr, dpr);

    const cx = displaySize / 2;
    const cy = displaySize / 2;
    const radius = displaySize * 0.38;
    const n = DIMENSIONS.length;
    const angleStep = (2 * Math.PI) / n;
    const startAngle = -Math.PI / 2; // Start at top

    radarCtx.clearRect(0, 0, displaySize, displaySize);

    // Draw grid rings
    const rings = [0.25, 0.5, 0.75, 1.0];
    radarCtx.strokeStyle = '#30363d';
    radarCtx.lineWidth = 0.5;
    rings.forEach(r => {
      radarCtx.beginPath();
      for (let i = 0; i <= n; i++) {
        const angle = startAngle + i * angleStep;
        const x = cx + Math.cos(angle) * radius * r;
        const y = cy + Math.sin(angle) * radius * r;
        if (i === 0) radarCtx.moveTo(x, y);
        else radarCtx.lineTo(x, y);
      }
      radarCtx.stroke();
    });

    // Draw axis lines and labels
    radarCtx.strokeStyle = '#30363d';
    radarCtx.lineWidth = 0.5;
    radarCtx.fillStyle = '#8b949e';
    radarCtx.font = '11px Inter, sans-serif';
    radarCtx.textAlign = 'center';
    radarCtx.textBaseline = 'middle';

    for (let i = 0; i < n; i++) {
      const angle = startAngle + i * angleStep;
      const lx = cx + Math.cos(angle) * radius;
      const ly = cy + Math.sin(angle) * radius;

      radarCtx.beginPath();
      radarCtx.moveTo(cx, cy);
      radarCtx.lineTo(lx, ly);
      radarCtx.stroke();

      // Label position outside the ring — adjust alignment based on angle
      const labelR = radius + 28;
      const lbx = cx + Math.cos(angle) * labelR;
      const lby = cy + Math.sin(angle) * labelR;

      // Dynamic text alignment so labels don't overlap the chart
      const angleDeg = (angle * 180 / Math.PI + 360) % 360;
      if (angleDeg > 85 && angleDeg < 95) {
        radarCtx.textAlign = 'center';
      } else if (angleDeg > 90 && angleDeg < 270) {
        radarCtx.textAlign = 'right';
      } else if (angleDeg > 265 && angleDeg < 275) {
        radarCtx.textAlign = 'center';
      } else {
        radarCtx.textAlign = 'left';
      }

      radarCtx.fillText(DIMENSIONS[i].short, lbx, lby);
    }

    // Reset text alignment for any future drawing
    radarCtx.textAlign = 'center';

    // Draw data polygons
    function drawPolygon(project, color, alpha) {
      radarCtx.beginPath();
      for (let i = 0; i <= n; i++) {
        const idx = i % n;
        const angle = startAngle + idx * angleStep;
        const val = capScore(project.capabilities[DIMENSIONS[idx].key]);
        const r = Math.max(val, 0.02) * radius; // Small minimum so shape is visible
        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;
        if (i === 0) radarCtx.moveTo(x, y);
        else radarCtx.lineTo(x, y);
      }
      radarCtx.closePath();
      radarCtx.fillStyle = color.replace('1)', alpha + ')');
      radarCtx.fill();
      radarCtx.strokeStyle = color;
      radarCtx.lineWidth = 2;
      radarCtx.stroke();

      // Draw dots at vertices
      for (let i = 0; i < n; i++) {
        const angle = startAngle + i * angleStep;
        const val = capScore(project.capabilities[DIMENSIONS[i].key]);
        const r = Math.max(val, 0.02) * radius;
        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;
        radarCtx.beginPath();
        radarCtx.arc(x, y, 3, 0, 2 * Math.PI);
        radarCtx.fillStyle = color;
        radarCtx.fill();
      }
    }

    // Project B drawn first (behind)
    drawPolygon(projectB, 'rgba(59, 130, 246, 1)', 0.12);
    // Project A drawn on top
    const colorA = projectA.id === 'champollion' ? 'rgba(240, 180, 41, 1)' : 'rgba(63, 185, 80, 1)';
    drawPolygon(projectA, colorA, 0.15);

    // Legend
    radarLegendEl.innerHTML = `
      <div class="legend-item">
        <div class="legend-swatch" style="background: ${colorA}"></div>
        <span>${projectA.name}</span>
      </div>
      <div class="legend-item">
        <div class="legend-swatch" style="background: rgba(59, 130, 246, 1)"></div>
        <span>${projectB.name}</span>
      </div>
    `;
  }

  // ── Scroll-Reveal Animation ───────────────────────────────────
  //
  // Uses IntersectionObserver to add .revealed class when sections
  // scroll into view. The CSS handles the opacity/transform transition.

  function initScrollReveal() {
    const sections = document.querySelectorAll('.reveal-section');
    if (!sections.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          // Stop observing once revealed — no re-hide on scroll up
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.15,
      rootMargin: '0px 0px -40px 0px',
    });

    sections.forEach(section => observer.observe(section));
  }

  // ── Mobile Navigation Toggle ──────────────────────────────────

  function initNavToggle() {
    if (!navToggle || !navLinks) return;

    navToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close menu when a nav link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // ── View Toggle ────────────────────────────────────────────────
  //
  // Both renderGrid() and renderTable() run on every filter/sort change
  // so both views stay in sync. setView() only toggles CSS display —
  // this means switching views is instant with no re-render delay.

  /**
   * Switch between 'cards' and 'table' views.
   * Does NOT re-render — both views are already up to date.
   */
  function setView(view) {
    activeView = view;

    // Toggle display of the two view containers
    gridEl.style.display = (view === 'cards') ? '' : 'none';
    tableViewEl.style.display = (view === 'table') ? '' : 'none';

    // Update button active states and ARIA
    document.querySelectorAll('.view-btn').forEach(btn => {
      const isActive = btn.dataset.view === view;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-checked', isActive ? 'true' : 'false');
    });
  }

  function initViewToggle() {
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', () => setView(btn.dataset.view));
    });
  }

  // ── Filter Event Handlers ──────────────────────────────────────

  // Category filters (mutually exclusive)
  document.getElementById('category-filters').addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;

    document.querySelectorAll('#category-filters .chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeCategory = chip.dataset.filter;

    renderGrid();
    renderTable();
  });

  // Capability filters (toggle, can have multiple)
  document.getElementById('capability-filters').addEventListener('click', (e) => {
    const chip = e.target.closest('.cap-chip');
    if (!chip) return;

    const cap = chip.dataset.cap;
    chip.classList.toggle('active');

    if (activeCapabilities.has(cap)) {
      activeCapabilities.delete(cap);
    } else {
      activeCapabilities.add(cap);
    }

    renderGrid();
    renderTable();
  });

  // Sort selector
  sortSelect.addEventListener('change', () => {
    sortMode = sortSelect.value;
    renderGrid();
    renderTable();
  });

  // Radar selectors
  radarSelectA.addEventListener('change', drawRadar);
  radarSelectB.addEventListener('change', drawRadar);

  // Redraw radar on window resize for responsiveness
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(drawRadar, 200);
  });

  // ── Initialize ─────────────────────────────────────────────────
  renderGrid();
  renderTable();
  populateRadarSelects();
  drawRadar();
  initScrollReveal();
  initNavToggle();
  initViewToggle();

})();
