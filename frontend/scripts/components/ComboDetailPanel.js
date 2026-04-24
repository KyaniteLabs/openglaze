/**
 * ComboDetailPanel - Slide-out detail panel for glaze combinations
 * Shows all combo data instantly (no API calls): warnings, prediction,
 * application instructions, side-by-side glaze details, food safety
 */
class ComboDetailPanel {
    constructor(container) {
        this.container = container || document.body;
        this.combo = null;
        this.baseGlaze = null;
        this.topGlaze = null;
        this.element = null;
        this.isOpen = false;
        this.render();
    }

    render() {
        // Backdrop
        this.backdrop = document.createElement('div');
        this.backdrop.className = 'combo-detail-backdrop';
        this.backdrop.style.display = 'none';
        this.backdrop.addEventListener('click', () => this.hide());

        // Panel
        this.element = document.createElement('div');
        this.element.className = 'combo-detail-panel';
        this.element.style.display = 'none';

        this.container.appendChild(this.backdrop);
        this.container.appendChild(this.element);
    }

    show(combo, baseGlaze, topGlaze) {
        this.combo = combo;
        this.baseGlaze = baseGlaze;
        this.topGlaze = topGlaze;

        this.element.innerHTML = this._buildHTML();
        this._attachEvents();

        this.backdrop.style.display = 'block';
        this.element.style.display = 'flex';
        this.isOpen = true;

        // Scroll to top
        const scrollable = this.element.querySelector('.combo-detail-scroll');
        if (scrollable) scrollable.scrollTop = 0;
    }

    hide() {
        this.backdrop.style.display = 'none';
        this.element.style.display = 'none';
        this.isOpen = false;
    }

    _buildHTML() {
        const combo = this.combo;
        const base = this.baseGlaze;
        const top = this.topGlaze;
        const warnings = this._getWarnings();
        const foodSafety = this._getFoodSafety();

        let html = '';

        // Header
        html += `
        <div class="combo-detail-header">
            <div class="combo-detail-header-top">
                <div class="combo-detail-swatches">
                    <div class="combo-detail-swatch" style="background-color: ${base?.hex || '#ccc'}" title="${combo.base}"></div>
                    <span class="combo-detail-swatch-arrow">&rarr;</span>
                    <div class="combo-detail-swatch" style="background-color: ${top?.hex || '#ccc'}" title="${combo.top}"></div>
                </div>
                <div class="combo-detail-header-info">
                    <h2 class="combo-detail-title">${combo.top} over ${combo.base}</h2>
                    <div class="combo-detail-badges">
                        <span class="badge badge-risk-${combo.risk || 'low'}">${(combo.risk || 'low').charAt(0).toUpperCase() + (combo.risk || 'low').slice(1)} Risk</span>
                        ${combo.type === 'proven' ? '<span class="badge badge-proven">Proven</span>' : '<span class="badge badge-hypothesis">Hypothesis</span>'}
                        ${foodSafety.badge}
                    </div>
                </div>
            </div>
            <button class="combo-detail-close">&times;</button>
        </div>`;

        // Scrollable body
        html += '<div class="combo-detail-scroll">';

        // Warnings
        if (warnings.length > 0) {
            html += '<div class="combo-detail-warnings">';
            warnings.forEach(w => {
                html += `<div class="combo-detail-warning-item">${w}</div>`;
            });
            html += '</div>';
        }

        // Prediction
        if (combo.result || combo.chemistry) {
            html += '<div class="combo-detail-section">';
            html += '<h3 class="combo-detail-section-title">Prediction</h3>';
            if (combo.result) {
                html += `<p class="combo-detail-result">${combo.result}</p>`;
            }
            if (combo.chemistry) {
                html += `<p class="combo-detail-chemistry">${combo.chemistry}</p>`;
            }
            if (combo.bestOn) {
                html += `<p class="combo-detail-best-on"><strong>Best on:</strong> ${combo.bestOn}</p>`;
            }
            html += '</div>';
        }

        // Application instructions
        if (combo.application) {
            html += '<div class="combo-detail-section">';
            html += '<h3 class="combo-detail-section-title">Application</h3>';
            html += `<p class="combo-detail-application">${combo.application}</p>`;
            html += '</div>';
        }

        // Photo section
        html += '<div class="combo-detail-section">';
        html += '<h3 class="combo-detail-section-title">Photo</h3>';
        html += '<div id="combo-detail-photo-area"></div>';
        html += '</div>';

        // Side-by-side glaze details
        html += '<div class="combo-detail-section">';
        html += '<h3 class="combo-detail-section-title">Glaze Details</h3>';
        html += '<div class="combo-detail-glazes-grid">';
        html += this._buildGlazeColumn(base, 'Base');
        html += this._buildGlazeColumn(top, 'Top');
        html += '</div>';
        html += '</div>';

        // UMF / Chemistry Analysis section
        html += '<div class="combo-detail-section" id="combo-umf-section">';
        html += '<h3 class="combo-detail-section-title">Unity Molecular Formula</h3>';
        html += '<div class="combo-umf-loading">Loading chemistry data...</div>';
        html += '<div class="combo-umf-grid" style="display:none;"></div>';
        html += '</div>';

        html += '</div>'; // end scroll

        // Footer
        html += `
        <div class="combo-detail-footer">
            <button class="btn btn-secondary combo-detail-ask-kama">Ask Kama about this combo</button>
            <button class="btn btn-primary combo-detail-close-btn">Close</button>
        </div>`;

        return html;
    }

    _buildGlazeColumn(glaze, role) {
        if (!glaze) {
            return `<div class="combo-detail-glaze-col">
                <p class="text-tertiary">Glaze data not available</p>
            </div>`;
        }

        let html = `<div class="combo-detail-glaze-col">`;
        html += `<div class="combo-detail-glaze-col-header">`;
        html += `<div class="combo-detail-glaze-mini-swatch" style="background-color: ${glaze.hex || '#ccc'}"></div>`;
        html += `<div>`;
        html += `<h4>${glaze.name}</h4>`;
        html += `<span class="combo-detail-role">${role}</span>`;
        if (glaze.family) html += `<span class="combo-detail-family">${glaze.family}</span>`;
        html += `</div></div>`;

        if (glaze.chemistry) {
            html += `<div class="combo-detail-glaze-field"><strong>Chemistry</strong><p>${glaze.chemistry}</p></div>`;
        }
        if (glaze.behavior) {
            html += `<div class="combo-detail-glaze-field"><strong>Behavior</strong><p>${glaze.behavior}</p></div>`;
        }
        if (glaze.layering) {
            html += `<div class="combo-detail-glaze-field"><strong>Layering</strong><p>${glaze.layering}</p></div>`;
        }
        if (glaze.warning) {
            html += `<div class="combo-detail-glaze-warning">${glaze.warning}</div>`;
        }
        if (glaze.recipe) {
            html += `<div class="combo-detail-glaze-field"><strong>Recipe</strong><pre>${glaze.recipe}</pre></div>`;
        }
        if (glaze.source) {
            html += `<p class="combo-detail-source">${glaze.source}</p>`;
        }

        html += '</div>';
        return html;
    }

    _getWarnings() {
        const warnings = [];
        const base = this.baseGlaze;
        const top = this.topGlaze;
        const combo = this.combo;

        // Combo-level warning
        if (combo.warning) {
            warnings.push(combo.warning);
        }

        // Glaze-level warnings
        if (base?.warning) {
            warnings.push(`<strong>${base.name}:</strong> ${base.warning}`);
        }
        if (top?.warning) {
            warnings.push(`<strong>${top.name}:</strong> ${top.warning}`);
        }

        // Client-side compatibility checks
        // Shino over non-shino → high crawl risk (but skip for proven combos)
        const baseIsShino = base?.family === 'Shinos';
        const topIsShino = top?.family === 'Shinos';
        const isProven = combo.type === 'proven' || combo.type === 'research-backed';
        if (topIsShino && !baseIsShino && !isProven) {
            warnings.push(`${top.name} (Shino) over ${base.name} has high crawl risk — Shinos shrink significantly and may pull away from glazes with different thermal expansion`);
        }

        // Both high in iron → may be too dark
        const baseHasIron = base?.chemistry?.toLowerCase().includes('iron');
        const topHasIron = top?.chemistry?.toLowerCase().includes('iron');
        if (baseHasIron && topHasIron) {
            warnings.push('Both glazes contain iron — result may be very dark or muddy');
        }

        // Copper in top glaze → reduction sensitive
        const topHasCopper = top?.chemistry?.toLowerCase().includes('copper');
        if (topHasCopper) {
            warnings.push(`${top.name} contains copper — color is highly reduction-sensitive; results vary with kiln atmosphere`);
        }

        return warnings;
    }

    _getFoodSafety() {
        const base = this.baseGlaze;
        const top = this.topGlaze;

        const baseSafe = base?.food_safe;
        const topSafe = top?.food_safe;

        if (baseSafe === true && topSafe === true) {
            return {
                badge: '<span class="badge badge-food-safe">Food Safe</span>',
                status: 'safe'
            };
        } else if (baseSafe === false || topSafe === false) {
            const reason = baseSafe === false ? base.name : top.name;
            return {
                badge: `<span class="badge badge-food-unsafe">Not Food Safe</span>`,
                status: 'unsafe'
            };
        } else {
            return {
                badge: '<span class="badge badge-food-unknown">Food Safety Unknown</span>',
                status: 'unknown'
            };
        }
    }

    _attachEvents() {
        // Close buttons
        const closeBtn = this.element.querySelector('.combo-detail-close');
        const closeBtnFooter = this.element.querySelector('.combo-detail-close-btn');
        if (closeBtn) closeBtn.addEventListener('click', () => this.hide());
        if (closeBtnFooter) closeBtnFooter.addEventListener('click', () => this.hide());

        // Ask Kama button
        const askKama = this.element.querySelector('.combo-detail-ask-kama');
        if (askKama) {
            askKama.addEventListener('click', () => {
                this.hide();
                const question = `Tell me more about layering ${this.combo.top} over ${this.combo.base}. What should I watch out for?`;
                if (window.kamaPanel) {
                    window.kamaPanel.open();
                    window.kamaPanel.input.value = question;
                    window.kamaPanel.input.focus();
                }
            });
        }

        // Photo upload area
        const photoArea = this.element.querySelector('#combo-detail-photo-area');
        if (photoArea) {
            if (this.combo.photo) {
                photoArea.innerHTML = `
                    <div class="combo-detail-photo">
                        <img src="/${this.combo.photo}" alt="${this.combo.top} over ${this.combo.base}">
                    </div>
                `;
            } else {
                photoArea.innerHTML = `
                    <button class="btn btn-secondary" id="combo-detail-add-photo">+ Add Photo</button>
                `;
                const addBtn = photoArea.querySelector('#combo-detail-add-photo');
                if (addBtn) {
                    addBtn.addEventListener('click', () => {
                        photoArea.innerHTML = '';
                        new PhotoUploadForm(photoArea, {
                            onSuccess: (url, path) => {
                                this.combo.photo = path;
                                photoArea.innerHTML = `
                                    <div class="combo-detail-photo">
                                        <img src="${url}" alt="${this.combo.top} over ${this.combo.base}">
                                    </div>
                                `;
                            },
                            onCancel: () => {
                                photoArea.innerHTML = `
                                    <button class="btn btn-secondary" id="combo-detail-add-photo">+ Add Photo</button>
                                `;
                                const newBtn = photoArea.querySelector('#combo-detail-add-photo');
                                if (newBtn) newBtn.addEventListener('click', arguments.callee);
                            }
                        });
                    });
                }
            }
        }

        // Fetch UMF data for both glazes
        this._fetchUMFData();
    }

    async _fetchUMFData() {
        const section = this.element.querySelector('#combo-umf-section');
        if (!section) return;

        const glazeNames = [];
        if (this.baseGlaze) glazeNames.push(this.baseGlaze.name);
        if (this.topGlaze) glazeNames.push(this.topGlaze.name);

        if (glazeNames.length === 0) {
            section.querySelector('.combo-umf-loading').textContent = 'No glaze data available for analysis.';
            return;
        }

        const results = {};
        const promises = glazeNames.map(async (name) => {
            try {
                const resp = await fetch(`/api/glazes/${encodeURIComponent(name)}/umf`);
                if (resp.ok) {
                    results[name] = await resp.json();
                } else {
                    results[name] = { success: false, error: 'Not available' };
                }
            } catch (e) {
                results[name] = { success: false, error: 'Failed to load' };
            }
        });

        await Promise.all(promises);
        this._renderUMF(results);
    }

    _renderUMF(results) {
        const section = this.element.querySelector('#combo-umf-section');
        if (!section) return;

        const loading = section.querySelector('.combo-umf-loading');
        const grid = section.querySelector('.combo-umf-grid');

        // Check if any glaze has UMF data
        const hasAny = Object.values(results).some(r => r.success && r.umf_formula);
        if (!hasAny) {
            loading.textContent = 'No recipe data available for UMF calculation.';
            return;
        }

        loading.style.display = 'none';
        grid.style.display = 'grid';

        let html = '';

        for (const [name, data] of Object.entries(results)) {
            if (!data.success || !data.umf_formula) {
                html += `<div class="combo-umf-card">
                    <h4>${name}</h4>
                    <p class="text-tertiary">${data.error || 'No recipe data'}</p>
                </div>`;
                continue;
            }

            const f = data.umf_formula;
            const r = data.ratios || {};
            const surface = this._formatSurface(data.surface_prediction);
            const warnings = (data.limit_warnings || []).filter(w => w);

            html += `<div class="combo-umf-card">`;
            html += `<h4>${name}</h4>`;

            // Surface prediction badge
            if (data.surface_prediction) {
                html += `<span class="combo-umf-surface ${surface.cls}">${surface.label}</span>`;
            }

            // Key ratios
            html += `<div class="combo-umf-ratios">`;
            if (r.sio2_al2o3) {
                html += `<div class="combo-umf-ratio">
                    <span class="combo-umf-ratio-label">SiO2:Al2O3</span>
                    <span class="combo-umf-ratio-value">${r.sio2_al2o3}</span>
                    <span class="combo-umf-ratio-desc">${this._interpretRatio('sio2_al2o3', r.sio2_al2o3)}</span>
                </div>`;
            }
            if (r.flux_al2o3) {
                html += `<div class="combo-umf-ratio">
                    <span class="combo-umf-ratio-label">Flux:Al2O3</span>
                    <span class="combo-umf-ratio-value">${r.flux_al2o3}</span>
                    <span class="combo-umf-ratio-desc">${this._interpretRatio('flux_al2o3', r.flux_al2o3)}</span>
                </div>`;
            }
            if (r.knao_cao !== undefined) {
                html += `<div class="combo-umf-ratio">
                    <span class="combo-umf-ratio-label">KNaO:CaO</span>
                    <span class="combo-umf-ratio-value">${r.knao_cao}</span>
                    <span class="combo-umf-ratio-desc">${this._interpretRatio('knao_cao', r.knao_cao)}</span>
                </div>`;
            }
            html += `</div>`;

            // UMF formula (fluxes + Al2O3 + SiO2)
            const oxideOrder = ['K2O', 'Na2O', 'Li2O', 'CaO', 'MgO', 'BaO', 'ZnO', 'SrO', 'FeO', 'MnO', 'Al2O3', 'SiO2', 'B2O3', 'TiO2', 'P2O5'];
            const presentOxides = oxideOrder.filter(ox => f[ox] !== undefined && f[ox] !== 0);

            if (presentOxides.length > 0) {
                html += `<div class="combo-umf-formula">`;
                html += `<strong>Formula</strong>`;
                for (const ox of presentOxides) {
                    const val = f[ox];
                    const isFlux = ox !== 'Al2O3' && ox !== 'SiO2' && ox !== 'B2O3' && ox !== 'TiO2' && ox !== 'P2O5';
                    const cls = isFlux ? '' : (ox === 'Al2O3' ? 'combo-umf-al2o3' : 'combo-umf-sio2');
                    html += `<span class="combo-umf-oxide ${cls}"><span class="combo-umf-oxide-name">${ox}</span> <span class="combo-umf-oxide-val">${val.toFixed(val >= 1 ? 2 : 3)}</span></span>`;
                }
                html += `</div>`;
            }

            // Limit warnings
            if (warnings.length > 0) {
                html += `<div class="combo-umf-warnings">`;
                warnings.forEach(w => {
                    html += `<div class="combo-umf-warning">⚠ ${w}</div>`;
                });
                html += `</div>`;
            }

            html += `</div>`;
        }

        grid.innerHTML = html;
    }

    _formatSurface(prediction) {
        const map = {
            'high_gloss': { label: 'High Gloss', cls: 'surface-glossy' },
            'glossy': { label: 'Glossy', cls: 'surface-glossy' },
            'satin': { label: 'Satin', cls: 'surface-satin' },
            'soft_matt': { label: 'Soft Matte', cls: 'surface-matte' },
            'dry_matt': { label: 'Dry Matte', cls: 'surface-matte' },
            'underfired': { label: 'Underfired', cls: 'surface-underfired' },
            'unstable': { label: 'Unstable', cls: 'surface-unstable' },
        };
        return map[prediction] || { label: prediction || 'Unknown', cls: '' };
    }

    _interpretRatio(name, value) {
        if (name === 'sio2_al2o3') {
            if (value < 3) return 'dry/matt';
            if (value < 5) return 'matt';
            if (value < 10) return 'glossy';
            return 'runny';
        }
        if (name === 'flux_al2o3') {
            if (value < 2) return 'dry/underfired';
            if (value < 3) return 'stable melt';
            return 'runny';
        }
        if (name === 'knao_cao') {
            if (value === 0) return 'no alkali';
            if (value < 0.5) return 'balanced';
            if (value < 1.5) return 'alkali-leaning';
            return 'high alkali';
        }
        return '';
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
        if (this.backdrop && this.backdrop.parentNode) {
            this.backdrop.parentNode.removeChild(this.backdrop);
        }
    }
}

window.ComboDetailPanel = ComboDetailPanel;
