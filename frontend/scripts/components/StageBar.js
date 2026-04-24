/**
 * StageBar - Horizontal navigation for pipeline stages
 * Filters combinations by their current stage
 */
class StageBar {
    constructor(container, stages, onStageChange) {
        this.container = container;
        this.stages = stages || ['idea', 'predicting', 'testing', 'fired', 'documented'];
        this.onStageChange = onStageChange;
        this.activeStage = this.stages[0];
        this.counts = {};
        this.element = null;
        this.render();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'stage-bar';

        this.stages.forEach((stage, index) => {
            const pill = document.createElement('button');
            pill.className = `stage-pill ${stage === this.activeStage ? 'active' : ''}`;
            pill.dataset.stage = stage;

            // Stage name
            const name = document.createElement('span');
            name.className = 'stage-name';
            name.textContent = this.formatStageName(stage);

            // Count badge
            const count = document.createElement('span');
            count.className = 'stage-count';
            count.textContent = this.counts[stage] || 0;

            pill.appendChild(name);
            pill.appendChild(count);

            pill.addEventListener('click', () => this.setActive(stage));

            this.element.appendChild(pill);
        });

        this.container.appendChild(this.element);
    }

    formatStageName(stage) {
        return stage.charAt(0).toUpperCase() + stage.slice(1);
    }

    setActive(stage) {
        if (this.activeStage === stage) return;

        this.activeStage = stage;

        // Update UI
        this.element.querySelectorAll('.stage-pill').forEach(pill => {
            pill.classList.toggle('active', pill.dataset.stage === stage);
        });

        if (this.onStageChange) {
            this.onStageChange(stage);
        }
    }

    updateCounts(counts) {
        this.counts = counts;
        this.element.querySelectorAll('.stage-pill').forEach(pill => {
            const stage = pill.dataset.stage;
            const countEl = pill.querySelector('.stage-count');
            if (countEl) {
                countEl.textContent = counts[stage] || 0;
            }
        });
    }

    getActiveStage() {
        return this.activeStage;
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

window.StageBar = StageBar;