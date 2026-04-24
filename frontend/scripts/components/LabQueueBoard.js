/**
 * LabQueueBoard - Open board grid of testable combos with claim/release
 */
class LabQueueBoard {
    constructor(container, studioId) {
        this.container = container;
        this.studioId = studioId;
        this.element = null;
        this.render();
        this._load();
    }

    async _load() {
        const queue = await API.getLabQueue(this.studioId);
        if (!queue) {
            this.element.innerHTML = '<p class="text-secondary">Could not load lab queue.</p>';
            return;
        }

        if (queue.length === 0) {
            this.element.innerHTML = `
                <div class="empty-state" style="display: flex;">
                    <div class="empty-icon">◇</div>
                    <h2>Lab queue is empty</h2>
                    <p>No testable combinations yet.</p>
                </div>
            `;
            return;
        }

        this._renderGrid(queue);
    }

    _renderGrid(queue) {
        const grid = document.createElement('div');
        grid.className = 'lab-queue-grid';

        queue.forEach(combo => {
            const card = document.createElement('div');
            card.className = 'lab-queue-card card';
            card.dataset.comboId = combo.id;

            const claim = combo.claim;
            const isMine = claim && claim.assigned_to === localStorage.getItem('simple_auth_user_id');
            const isClaimed = claim && (claim.status === 'claimed' || claim.status === 'in_progress');

            card.innerHTML = `
                <div class="lab-queue-swatches">
                    <div class="combo-swatch-base" style="background-color: var(--color-${this._familyColor(combo.base)})"></div>
                    <div class="combo-swatch-top" style="background-color: var(--color-${this._familyColor(combo.top)})"></div>
                </div>
                <div class="lab-queue-info">
                    <h4>${combo.top} over ${combo.base}</h4>
                    <div class="lab-queue-badges">
                        <span class="badge badge-${combo.prediction_grade || 'unknown'}">${combo.prediction_grade || 'unknown'}</span>
                        ${combo.risk ? `<span class="badge badge-risk-${combo.risk}">${combo.risk} risk</span>` : ''}
                    </div>
                    ${isClaimed ? `
                        <div class="lab-claim-status">
                            ${isMine ? 'Claimed by you' : `Claimed by ${claim.claimed_by_name || 'someone'}`}
                            ${claim.claimed_at ? ` — ${this._timeAgo(claim.claimed_at)}` : ''}
                        </div>
                        ${isMine ? `
                            <div class="lab-queue-actions">
                                <button class="btn btn-primary btn-small lab-complete-btn" data-id="${combo.id}">Complete Test</button>
                                <button class="btn btn-secondary btn-small lab-release-btn" data-id="${combo.id}">Release</button>
                            </div>
                        ` : ''}
                    ` : `
                        <div class="lab-queue-actions">
                            <button class="btn btn-primary btn-small lab-claim-btn" data-id="${combo.id}">Claim</button>
                        </div>
                    `}
                </div>
            `;

            // Wire buttons
            const claimBtn = card.querySelector('.lab-claim-btn');
            const releaseBtn = card.querySelector('.lab-release-btn');
            const completeBtn = card.querySelector('.lab-complete-btn');

            if (claimBtn) {
                claimBtn.addEventListener('click', () => this._claim(combo.id, card));
            }
            if (releaseBtn) {
                releaseBtn.addEventListener('click', () => this._release(combo.id, card));
            }
            if (completeBtn) {
                completeBtn.addEventListener('click', () => this._openFiringLog(combo));
            }

            grid.appendChild(card);
        });

        this.element.innerHTML = '';
        const header = document.createElement('h3');
        header.textContent = `Lab Queue (${queue.length} combos)`;
        this.element.appendChild(header);
        this.element.appendChild(grid);
    }

    async _claim(comboId, card) {
        const result = await API.claimCombo(this.studioId, comboId);
        if (result) {
            this._load(); // Refresh grid
        } else {
            alert('Could not claim — may already be taken.');
        }
    }

    async _release(comboId) {
        await API.releaseCombo(this.studioId, comboId);
        this._load();
    }

    _openFiringLog(combo) {
        if (window.FiringLogForm) {
            new FiringLogForm(combo, this.studioId, () => this._load());
        }
    }

    _familyColor(glazeName) {
        if (!glazeName) return 'gray';
        const name = glazeName.toLowerCase();
        if (name.includes('red') || name.includes('iron')) return 'reds';
        if (name.includes('yellow') || name.includes('celadon')) return 'yellows';
        if (name.includes('green') || name.includes('jade')) return 'greens';
        if (name.includes('blue') || name.includes('chun') || name.includes('cobalt')) return 'blues';
        if (name.includes('purple') || name.includes('lavender')) return 'purples';
        if (name.includes('brown') || name.includes('tenmoku') || name.includes('oil spot')) return 'browns';
        if (name.includes('shino')) return 'shinos';
        if (name.includes('white') || name.includes('snow') || name.includes('cotton')) return 'whites';
        if (name.includes('clear') || name.includes('gloss') || name.includes('transparent')) return 'clears';
        return 'gray';
    }

    _timeAgo(dateStr) {
        const now = Date.now();
        const then = new Date(dateStr).getTime();
        const diff = now - then;
        const days = Math.floor(diff / 86400000);
        if (days < 1) return 'today';
        if (days === 1) return 'yesterday';
        if (days < 7) return `${days} days ago`;
        return `${Math.floor(days / 7)} weeks ago`;
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'lab-queue-board';
        this.container.appendChild(this.element);
    }
}

window.LabQueueBoard = LabQueueBoard;
