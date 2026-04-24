/**
 * ComboCard - Card component for displaying glaze combinations
 * Shows overlapping swatches, title, prediction, and status badges
 */
class ComboCard {
    constructor(container, combo) {
        this.container = container;
        this.combo = combo;
        this.element = null;
        this.render();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'combo-card card';
        this.element.dataset.id = this.combo.id;
        this.element.draggable = true;

        // Swatches container (overlapping circles)
        const swatches = document.createElement('div');
        swatches.className = 'combo-swatches';
        swatches.style.position = 'relative';

        // Base swatch (larger, behind)
        const baseSwatch = document.createElement('div');
        baseSwatch.className = 'combo-swatch-base';
        baseSwatch.style.backgroundColor = this.combo.baseColor || '#7EB09B';
        baseSwatch.title = this.combo.base;

        // Top swatch (smaller, in front)
        const topSwatch = document.createElement('div');
        topSwatch.className = 'combo-swatch-top';
        topSwatch.style.backgroundColor = this.combo.topColor || '#C65D5B';
        topSwatch.title = this.combo.top;

        swatches.appendChild(baseSwatch);
        swatches.appendChild(topSwatch);

        // Photo badge if combo has a photo
        if (this.combo.photo) {
            const badge = document.createElement('span');
            badge.className = 'combo-photo-badge';
            badge.textContent = '📷';
            badge.title = 'Has photo';
            swatches.appendChild(badge);
        }

        // Info section
        const info = document.createElement('div');
        info.className = 'combo-info';

        // Title
        const title = document.createElement('h3');
        title.className = 'combo-title text-lg';
        title.textContent = `${this.combo.top} over ${this.combo.base}`;

        // Prediction preview
        const prediction = document.createElement('p');
        prediction.className = 'combo-prediction text-secondary';
        prediction.textContent = this.combo.prediction || this.combo.result || 'Click to see prediction';
        if (!this.combo.prediction && !this.combo.result) {
            prediction.classList.add('text-tertiary');
        }

        // Badges row
        const badges = document.createElement('div');
        badges.className = 'combo-badges';

        // Prediction grade badge
        const grade = this.combo.prediction_grade || 'unknown';
        const gradeBadge = document.createElement('span');
        gradeBadge.className = `badge badge-grade-${grade}`;
        gradeBadge.textContent = this.formatGrade(grade);

        const riskBadge = document.createElement('span');
        const risk = this.combo.risk || 'low';
        riskBadge.className = `badge badge-risk-${risk}`;
        riskBadge.textContent = `${risk.charAt(0).toUpperCase() + risk.slice(1)} Risk`;

        badges.appendChild(gradeBadge);
        badges.appendChild(riskBadge);

        info.appendChild(title);
        info.appendChild(prediction);
        info.appendChild(badges);

        this.element.appendChild(swatches);
        this.element.appendChild(info);

        // Click to open detail
        this.element.addEventListener('click', () => {
            this.container.dispatchEvent(new CustomEvent('combo-selected', {
                detail: { combo: this.combo },
                bubbles: true
            }));
        });

        // Drag events
        this.element.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', this.combo.id);
            this.element.classList.add('dragging');
        });

        this.element.addEventListener('dragend', () => {
            this.element.classList.remove('dragging');
        });

        this.container.appendChild(this.element);
    }

    formatStage(stage) {
        const stages = {
            'idea': 'Idea',
            'predicting': 'Predicting',
            'testing': 'Testing',
            'fired': 'Fired',
            'documented': 'Documented',
        };
        return stages[stage] || stage;
    }

    formatGrade(grade) {
        const grades = {
            'likely': 'Likely',
            'possible': 'Possible',
            'unlikely': 'Unlikely',
            'unknown': 'Unknown',
            'confirmed': 'Confirmed',
            'surprise': 'Surprise',
        };
        return grades[grade] || grade;
    }

    setStage(stage) {
        this.combo.stage = stage;
        // No-op: stage is no longer shown as primary badge
    }

    setPrediction(prediction) {
        this.combo.prediction = prediction;
        const el = this.element.querySelector('.combo-prediction');
        if (el) {
            el.textContent = prediction;
            el.classList.remove('text-tertiary');
        }
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

window.ComboCard = ComboCard;
