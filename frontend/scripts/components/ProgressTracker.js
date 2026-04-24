/**
 * ProgressTracker - Progress bar, combo status breakdown, stats summary
 */
class ProgressTracker {
    constructor(container) {
        this.container = container;
        this.element = null;
        this.render();
        this.fetch();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'progress-tracker';

        this.element.innerHTML = `
            <div class="pt-header">
                <h3 class="pt-title">Progress Dashboard</h3>
            </div>
            <div class="pt-progress-bar" id="pt-progress-bar">
                <div class="pt-bar-track">
                    <div class="pt-bar-fill" id="pt-bar-fill" style="width: 0%"></div>
                </div>
                <div class="pt-bar-label">
                    <span id="pt-bar-text">Loading...</span>
                </div>
            </div>
            <div class="pt-stats-grid" id="pt-stats">
                <div class="pt-stat-card">
                    <span class="pt-stat-value" id="pt-total">--</span>
                    <span class="pt-stat-label">Total Combos</span>
                </div>
                <div class="pt-stat-card">
                    <span class="pt-stat-value" id="pt-tested">--</span>
                    <span class="pt-stat-label">Tested</span>
                </div>
                <div class="pt-stat-card">
                    <span class="pt-stat-value" id="pt-research">--</span>
                    <span class="pt-stat-label">Research-Backed</span>
                </div>
                <div class="pt-stat-card">
                    <span class="pt-stat-value" id="pt-predictions">--</span>
                    <span class="pt-stat-label">Predictions</span>
                </div>
            </div>
            <div class="pt-stages" id="pt-stages">
                <h4 class="gam-section-title">By Stage</h4>
                <div id="pt-stage-list" class="pt-stage-list">
                    <div class="gam-loading">Loading...</div>
                </div>
            </div>
        `;
        this.container.appendChild(this.element);
    }

    async fetch() {
        try {
            const res = await fetch('/api/progress');
            if (!res.ok) return;
            const data = await res.json();
            this.renderData(data);
        } catch (e) {
            console.error('Progress fetch error:', e);
        }
    }

    renderData(data) {
        const total = data.total_combos || 0;
        const tested = data.tested_combos || 0;
        const pct = total > 0 ? Math.round((tested / total) * 100) : 0;

        // Progress bar
        document.getElementById('pt-bar-fill').style.width = pct + '%';
        document.getElementById('pt-bar-text').textContent = `${tested} / ${total} tested (${pct}%)`;

        // Stats
        document.getElementById('pt-total').textContent = total;
        document.getElementById('pt-tested').textContent = tested;
        document.getElementById('pt-research').textContent = data.research_combos || 0;
        document.getElementById('pt-predictions').textContent = data.prediction_combos || 0;

        // Stage breakdown
        const stageEl = document.getElementById('pt-stage-list');
        const stages = data.stage_breakdown || {};
        const stageColors = {
            idea: 'var(--amber)',
            hypothesis: 'var(--coral)',
            documented: 'var(--celadon)',
            tested: 'var(--terracotta)',
            proven: 'var(--terracotta)',
            confirmed: 'var(--celadon)',
        };
        if (Object.keys(stages).length) {
            stageEl.innerHTML = Object.entries(stages).map(([stage, count]) => `
                <div class="pt-stage-row">
                    <span class="pt-stage-dot" style="background: ${stageColors[stage] || 'var(--border)'}"></span>
                    <span class="pt-stage-name">${stage}</span>
                    <span class="pt-stage-count">${count}</span>
                </div>
            `).join('');
        } else {
            stageEl.innerHTML = '<div class="gam-empty">No combinations yet</div>';
        }
    }
}
