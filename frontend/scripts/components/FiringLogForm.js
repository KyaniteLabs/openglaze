/**
 * FiringLogForm - Modal form for recording firing results
 */
class FiringLogForm {
    constructor(combo, studioId, onComplete) {
        this.combo = combo;
        this.studioId = studioId;
        this.onComplete = onComplete;
        this.element = null;
        this.optionalExpanded = false;
        this.rating = 0;
        this.render();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'modal';
        this.element.style.display = 'flex';

        this.element.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content firing-log-modal">
                <div class="modal-header">
                    <h2>Firing Log: ${this.combo.top} over ${this.combo.base}</h2>
                    <button class="modal-close" id="firing-close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="firing-required">
                        <h4>Required *</h4>
                        <div class="form-group">
                            <label>Clay Body *</label>
                            <input type="text" id="firing-clay" class="form-input"
                                   placeholder="e.g., B-Mix, Porcelain, Raku clay" required>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Firing Type *</label>
                                <select id="firing-type" class="form-input" required>
                                    <option value="">Select...</option>
                                    <option value="electric">Electric</option>
                                    <option value="gas_reduction">Gas Reduction</option>
                                    <option value="gas_oxidation">Gas Oxidation</option>
                                    <option value="wood">Wood</option>
                                    <option value="salt">Salt/Soda</option>
                                    <option value="raku">Raku</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Cone *</label>
                                <select id="firing-cone" class="form-input" required>
                                    <option value="">Select...</option>
                                    <option value="04">04</option>
                                    <option value="06">06</option>
                                    <option value="5">5</option>
                                    <option value="6">6</option>
                                    <option value="8">8</option>
                                    <option value="10">10</option>
                                    <option value="12">12</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Confirmation *</label>
                            <div class="confirmation-toggle">
                                <button class="btn btn-toggle" data-value="confirmed" id="confirm-confirmed">Confirmed</button>
                                <button class="btn btn-toggle" data-value="surprise" id="confirm-surprise">Surprise</button>
                            </div>
                        </div>
                    </div>

                    <div class="firing-optional-toggle">
                        <button class="btn btn-ghost" id="toggle-optional">
                            <span class="toggle-arrow">&#9654;</span> Optional details
                        </button>
                    </div>

                    <div class="firing-optional" id="optional-section" style="display: none;">
                        <div class="form-group">
                            <label>Application Method</label>
                            <input type="text" id="firing-application" class="form-input"
                                   placeholder="e.g., dipping, spraying, brushing">
                        </div>
                        <div class="form-group">
                            <label>Thickness</label>
                            <input type="text" id="firing-thickness" class="form-input"
                                   placeholder="e.g., thin, medium, thick">
                        </div>
                        <div class="form-group">
                            <label>Drying Time</label>
                            <input type="text" id="firing-drying" class="form-input"
                                   placeholder="e.g., 1 hour, overnight">
                        </div>
                        <div class="form-group">
                            <label>Cooling Notes</label>
                            <textarea id="firing-cooling" class="form-input"
                                      placeholder="How did it cool down?"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Atmosphere Notes</label>
                            <textarea id="firing-atmosphere" class="form-input"
                                      placeholder="Reduction/oxidation details, any unusual atmosphere conditions"></textarea>
                        </div>
                    </div>

                    <div class="firing-result-section">
                        <div class="form-group">
                            <label>Rating</label>
                            <div class="star-rating" id="firing-rating">
                                ${[1,2,3,4,5].map(i => `<button class="star" data-value="${i}">&#9733;</button>`).join('')}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Result Description</label>
                            <textarea id="firing-result" class="form-input"
                                      placeholder="Describe what you see on the fired tile..."></textarea>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="firing-cancel-btn">Cancel</button>
                    <button class="btn btn-primary" id="firing-submit-btn">Submit Firing Log</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.element);
        this._wireEvents();
    }

    _wireEvents() {
        // Close
        this.element.querySelector('#firing-close-btn').addEventListener('click', () => this.destroy());
        this.element.querySelector('#firing-cancel-btn').addEventListener('click', () => this.destroy());
        this.element.querySelector('.modal-backdrop').addEventListener('click', () => this.destroy());

        // Toggle optional section
        this.element.querySelector('#toggle-optional').addEventListener('click', () => {
            this.optionalExpanded = !this.optionalExpanded;
            const section = this.element.querySelector('#optional-section');
            const arrow = this.element.querySelector('.toggle-arrow');
            section.style.display = this.optionalExpanded ? 'block' : 'none';
            arrow.innerHTML = this.optionalExpanded ? '&#9660;' : '&#9654;';
        });

        // Confirmation toggle
        let selectedConfirmation = null;
        const confirmBtns = this.element.querySelectorAll('.btn-toggle');
        confirmBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                confirmBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedConfirmation = btn.dataset.value;
            });
        });

        // Star rating
        const stars = this.element.querySelectorAll('.star');
        stars.forEach(star => {
            star.addEventListener('click', () => {
                this.rating = parseInt(star.dataset.value);
                stars.forEach((s, i) => {
                    s.classList.toggle('active', i < this.rating);
                });
            });
            star.addEventListener('mouseenter', () => {
                const val = parseInt(star.dataset.value);
                stars.forEach((s, i) => {
                    s.classList.toggle('hover', i < val);
                });
            });
        });
        this.element.querySelector('.star-rating').addEventListener('mouseleave', () => {
            stars.forEach((s, i) => {
                s.classList.remove('hover');
                s.classList.toggle('active', i < this.rating);
            });
        });

        // Submit
        this.element.querySelector('#firing-submit-btn').addEventListener('click', async () => {
            const clayBody = (this.element.querySelector('#firing-clay').value || '').trim();
            const firingType = this.element.querySelector('#firing-type').value;
            const cone = this.element.querySelector('#firing-cone').value;

            if (!clayBody || !firingType || !cone || !selectedConfirmation) {
                alert('Please fill in all required fields (Clay Body, Firing Type, Cone, Confirmation).');
                return;
            }

            const logData = {
                clay_body: clayBody,
                firing_type: firingType,
                cone: cone,
                confirmation: selectedConfirmation,
                studio_id: this.studioId,
            };

            // Optional fields
            const app = this.element.querySelector('#firing-application').value.trim();
            if (app) logData.application_method = app;
            const thick = this.element.querySelector('#firing-thickness').value.trim();
            if (thick) logData.thickness = thick;
            const drying = this.element.querySelector('#firing-drying').value.trim();
            if (drying) logData.drying_time = drying;
            const cooling = this.element.querySelector('#firing-cooling').value.trim();
            if (cooling) logData.cooling_notes = cooling;
            const atmosphere = this.element.querySelector('#firing-atmosphere').value.trim();
            if (atmosphere) logData.atmosphere_notes = atmosphere;
            if (this.rating) logData.rating = this.rating;
            const result = this.element.querySelector('#firing-result').value.trim();
            if (result) logData.result = result;

            // Create experiment + submit firing log
            const expData = {
                base_glaze: this.combo.base,
                top_glaze: this.combo.top,
                combination_id: this.combo.id,
                stage: 'firing',
                status: 'in_progress',
            };

            try {
                // Use the experiment API to create, then log
                const createResp = await fetch('/api/experiments', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('simple_auth_token')}`,
                    },
                    method: 'POST',
                    body: JSON.stringify(expData),
                });
                if (!createResp.ok) throw new Error('Failed to create experiment');
                const created = await createResp.json();

                // Submit firing log
                const logResp = await fetch(`/api/experiments/${created.id}/firing-log`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('simple_auth_token')}`,
                    },
                    method: 'POST',
                    body: JSON.stringify(logData),
                });
                if (!logResp.ok) throw new Error('Failed to submit firing log');

                this.destroy();
                if (this.onComplete) this.onComplete();
            } catch (e) {
                alert('Error: ' + e.message);
            }
        });

        // Escape key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.destroy();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

window.FiringLogForm = FiringLogForm;
