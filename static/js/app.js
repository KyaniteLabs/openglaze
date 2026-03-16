/**
 * OpenGlaze - Frontend Application
 * Vanilla JavaScript for maximum portability
 */

// API Base URL
const API_BASE = '/api';

// State
const state = {
    user: null,
    glazes: [],
    currentView: 'glazes',
    loading: false,
    editingGlazeId: null
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    checkAuth();

    // Check if we're on the dashboard page
    if (document.getElementById('glaze-grid')) {
        // Dashboard page - will be initialized by inline script
    } else {
        // Landing page
        loadTemplates();
        setupEventListeners();
    }

    setupThemeToggle();
});

// =============================================================================
// THEME MANAGEMENT
// =============================================================================

function initTheme() {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
}

function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

// =============================================================================
// AUTHENTICATION
// =============================================================================

async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/me`, {
            credentials: 'include'
        });

        if (response.ok) {
            state.user = await response.json();
            updateAuthUI(true);
        } else {
            state.user = null;
            updateAuthUI(false);
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        updateAuthUI(false);
    }
}

function updateAuthUI(isAuthenticated) {
    const authContainer = document.getElementById('nav-auth');

    if (!authContainer) return;

    if (isAuthenticated && state.user) {
        authContainer.innerHTML = `
            <span class="user-greeting">Hi, ${state.user.studio_name || state.user.email}</span>
            <a href="/dashboard" class="btn btn-primary">Dashboard</a>
            <a href="/auth/logout" class="btn btn-secondary">Log Out</a>
        `;
    } else {
        authContainer.innerHTML = `
            <a href="/auth/login" class="btn btn-ghost">Log In</a>
            <a href="/auth/register" class="btn btn-primary">Get Started</a>
        `;
    }
}

// =============================================================================
// DASHBOARD INITIALIZATION
// =============================================================================

async function initDashboard() {
    setupDashboardNavigation();
    setupFilters();
    await loadGlazes();
    updateDashboardAuth();
}

function setupDashboardNavigation() {
    const sidebarLinks = document.querySelectorAll('.sidebar-link');

    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.dataset.view;
            navigateToView(view);
        });
    });

    // Handle hash navigation
    const hash = window.location.hash.slice(1);
    if (hash && ['glazes', 'firings', 'import', 'settings'].includes(hash)) {
        navigateToView(hash);
    }
}

function navigateToView(view) {
    // Update state
    state.currentView = view;

    // Update sidebar active state
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.toggle('active', link.dataset.view === view);
    });

    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));

    // Show selected view
    const viewElement = document.getElementById(`view-${view}`);
    if (viewElement) {
        viewElement.classList.remove('hidden');
    }

    // Update URL hash
    window.location.hash = view;
}

function updateDashboardAuth() {
    const authContainer = document.getElementById('nav-auth');
    if (!authContainer) return;

    if (state.user) {
        authContainer.innerHTML = `
            <a href="/auth/logout" class="btn btn-secondary">Log Out</a>
        `;
    }
}

// =============================================================================
// GLAZES
// =============================================================================

async function loadGlazes() {
    try {
        const response = await fetch(`${API_BASE}/glazes`, {
            credentials: 'include'
        });

        if (response.ok) {
            state.glazes = await response.json();
            renderGlazes();
        } else if (response.status === 401) {
            // Not authenticated - show demo data in dashboard
            const demoResponse = await fetch(`${API_BASE}/demo/glazes`);
            if (demoResponse.ok) {
                state.glazes = await demoResponse.json();
                state.isDemo = true;
                renderGlazes();
                showDemoBanner();
            } else {
                // Fallback: redirect to login
                window.location.href = '/auth/login';
            }
        }
    } catch (error) {
        console.error('Failed to load glazes:', error);
        showNotification('Failed to load glazes', 'error');
    }
}

function showDemoBanner() {
    const header = document.querySelector('.content-header');
    if (header && !document.getElementById('demo-banner')) {
        const banner = document.createElement('div');
        banner.id = 'demo-banner';
        banner.style.cssText = 'background: linear-gradient(135deg, var(--color-accent), #b87333); color: white; padding: var(--space-3) var(--space-4); border-radius: var(--radius-lg); margin-bottom: var(--space-4); font-size: var(--text-sm); display: flex; align-items: center; justify-content: space-between; gap: var(--space-4);';
        banner.innerHTML = `
            <span>🎨 Demo mode - Sign in to save your own glazes</span>
            <a href="/auth/register" class="btn btn-sm" style="background: white; color: var(--color-accent);">Sign Up Free</a>
        `;
        header.parentNode.insertBefore(banner, header.nextSibling);
    }
}

function renderGlazes() {
    const grid = document.getElementById('glaze-grid');
    const emptyState = document.getElementById('empty-state');

    if (!grid) return;

    if (state.glazes.length === 0) {
        grid.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';

    grid.innerHTML = state.glazes.map(glaze => createGlazeCard(glaze)).join('');
}

function createGlazeCard(glaze) {
    const colorMap = {
        'green': { color: '#7eb8a2', dark: '#5a9078' },
        'blue': { color: '#5a8fd4', dark: '#2c5aa0' },
        'brown': { color: '#c17a4a', dark: '#8b4513' },
        'white': { color: '#f5f5f5', dark: '#e0e0e0' },
        'black': { color: '#333333', dark: '#1a1a1a' },
        'red': { color: '#c45c4a', dark: '#a04a3a' },
        'yellow': { color: '#d4a574', dark: '#b89060' },
        'purple': { color: '#8b6aa0', dark: '#6b4a80' }
    };

    const colors = colorMap[glaze.color?.toLowerCase()] || { color: '#9c8a70', dark: '#7a6b55' };

    return `
        <div class="glaze-card card card-hover" data-glaze-id="${glaze.id}" onclick="OpenGlaze.editGlaze('${glaze.id}')">
            <div class="glaze-swatch">
                <div class="glaze-swatch-color" style="--swatch-color: ${colors.color}; --swatch-color-dark: ${colors.dark};"></div>
                <div class="glaze-swatch-overlay"></div>
                <div class="glaze-actions">
                    <button class="glaze-action-btn" onclick="event.stopPropagation(); OpenGlaze.duplicateGlaze('${glaze.id}')" title="Duplicate">
                        ⧉
                    </button>
                    <button class="glaze-action-btn" onclick="event.stopPropagation(); OpenGlaze.deleteGlaze('${glaze.id}')" title="Delete">
                        🗑
                    </button>
                </div>
            </div>
            <div class="glaze-name">${escapeHtml(glaze.name)}</div>
            <div class="glaze-meta">
                <span class="badge badge-primary">Cone ${glaze.cone}</span>
                <span class="badge">${glaze.atmosphere}</span>
            </div>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// =============================================================================
// GLAZE MODAL
// =============================================================================

function openGlazeModal(glazeId = null) {
    const modal = document.getElementById('glaze-modal');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('glaze-form');
    const ingredientList = document.getElementById('ingredient-list');

    if (!modal || !form) return;

    state.editingGlazeId = glazeId;

    // Reset form
    form.reset();

    // Clear ingredients except one row
    ingredientList.innerHTML = `
        <div class="ingredient-row">
            <input type="text" class="input" name="ingredient_name[]" placeholder="Material name">
            <input type="number" class="input" name="ingredient_amount[]" placeholder="%" step="0.1">
            <button type="button" class="btn btn-ghost btn-sm" onclick="this.parentElement.remove()">&times;</button>
        </div>
    `;

    if (glazeId) {
        title.textContent = 'Edit Glaze';
        // Load glaze data
        const glaze = state.glazes.find(g => g.id === glazeId);
        if (glaze) {
            populateGlazeForm(glaze);
        }
    } else {
        title.textContent = 'New Glaze';
    }

    modal.classList.add('active');
}

function closeGlazeModal() {
    const modal = document.getElementById('glaze-modal');
    if (modal) {
        modal.classList.remove('active');
    }
    state.editingGlazeId = null;
}

function populateGlazeForm(glaze) {
    const form = document.getElementById('glaze-form');
    const ingredientList = document.getElementById('ingredient-list');

    // Fill basic fields
    form.querySelector('[name="name"]').value = glaze.name || '';
    form.querySelector('[name="cone"]').value = glaze.cone || '6';
    form.querySelector('[name="atmosphere"]').value = glaze.atmosphere || 'oxidation';
    form.querySelector('[name="base_type"]').value = glaze.base_type || 'clear';
    form.querySelector('[name="surface"]').value = glaze.surface || 'glossy';
    form.querySelector('[name="color"]').value = glaze.color || '';
    form.querySelector('[name="transparency"]').value = glaze.transparency || 'transparent';
    form.querySelector('[name="notes"]').value = glaze.notes || '';

    // Fill ingredients
    if (glaze.ingredients && glaze.ingredients.length > 0) {
        ingredientList.innerHTML = glaze.ingredients.map(ing => `
            <div class="ingredient-row">
                <input type="text" class="input" name="ingredient_name[]" value="${escapeHtml(ing.name)}" placeholder="Material name">
                <input type="number" class="input" name="ingredient_amount[]" value="${ing.amount}" placeholder="%" step="0.1">
                <button type="button" class="btn btn-ghost btn-sm" onclick="this.parentElement.remove()">&times;</button>
            </div>
        `).join('');
    }
}

function addIngredientRow() {
    const ingredientList = document.getElementById('ingredient-list');
    if (!ingredientList) return;

    const row = document.createElement('div');
    row.className = 'ingredient-row';
    row.innerHTML = `
        <input type="text" class="input" name="ingredient_name[]" placeholder="Material name">
        <input type="number" class="input" name="ingredient_amount[]" placeholder="%" step="0.1">
        <button type="button" class="btn btn-ghost btn-sm" onclick="this.parentElement.remove()">&times;</button>
    `;
    ingredientList.appendChild(row);
}

async function saveGlaze() {
    const form = document.getElementById('glaze-form');
    if (!form) return;

    const formData = new FormData(form);
    const ingredients = [];

    const names = formData.getAll('ingredient_name[]');
    const amounts = formData.getAll('ingredient_amount[]');

    names.forEach((name, i) => {
        if (name && amounts[i]) {
            ingredients.push({
                name: name,
                amount: parseFloat(amounts[i])
            });
        }
    });

    const glazeData = {
        name: formData.get('name'),
        cone: formData.get('cone'),
        atmosphere: formData.get('atmosphere'),
        base_type: formData.get('base_type'),
        surface: formData.get('surface'),
        color: formData.get('color'),
        transparency: formData.get('transparency'),
        notes: formData.get('notes'),
        ingredients: ingredients
    };

    try {
        let response;
        if (state.editingGlazeId) {
            response = await fetch(`${API_BASE}/glazes/${state.editingGlazeId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(glazeData)
            });
        } else {
            response = await fetch(`${API_BASE}/glazes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(glazeData)
            });
        }

        if (response.ok) {
            showNotification(state.editingGlazeId ? 'Glaze updated!' : 'Glaze created!', 'success');
            closeGlazeModal();
            await loadGlazes();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to save glaze', 'error');
        }
    } catch (error) {
        console.error('Save glaze error:', error);
        showNotification('Failed to save glaze', 'error');
    }
}

async function editGlaze(glazeId) {
    openGlazeModal(glazeId);
}

async function duplicateGlaze(glazeId) {
    const glaze = state.glazes.find(g => g.id === glazeId);
    if (!glaze) return;

    const newGlaze = {
        ...glaze,
        name: `${glaze.name} (Copy)`
    };
    delete newGlaze.id;

    try {
        const response = await fetch(`${API_BASE}/glazes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(newGlaze)
        });

        if (response.ok) {
            showNotification('Glaze duplicated!', 'success');
            await loadGlazes();
        }
    } catch (error) {
        console.error('Duplicate error:', error);
        showNotification('Failed to duplicate glaze', 'error');
    }
}

async function deleteGlaze(glazeId) {
    if (!confirm('Are you sure you want to delete this glaze?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/glazes/${glazeId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            showNotification('Glaze deleted', 'success');
            await loadGlazes();
        } else {
            showNotification('Failed to delete glaze', 'error');
        }
    } catch (error) {
        console.error('Delete glaze error:', error);
        showNotification('Failed to delete glaze', 'error');
    }
}

// =============================================================================
// FILTERS
// =============================================================================

function setupFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterGlazes(btn.dataset.filter);
        });
    });

    // Search
    const searchInput = document.getElementById('glaze-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            searchGlazes(e.target.value);
        }, 300));
    }
}

function filterGlazes(filter) {
    const grid = document.getElementById('glaze-grid');
    if (!grid) return;

    const cards = grid.querySelectorAll('.glaze-card');

    cards.forEach(card => {
        const glaze = state.glazes.find(g => g.id === card.dataset.glazeId);
        if (!glaze) return;

        let show = true;
        if (filter === 'cone6') show = glaze.cone === '6';
        else if (filter === 'cone10') show = glaze.cone === '10';
        else if (filter === 'reduction') show = glaze.atmosphere === 'reduction';
        else if (filter === 'oxidation') show = glaze.atmosphere === 'oxidation';

        card.style.display = show ? 'block' : 'none';
    });
}

function searchGlazes(query) {
    const grid = document.getElementById('glaze-grid');
    if (!grid) return;

    const cards = grid.querySelectorAll('.glaze-card');
    const lowerQuery = query.toLowerCase();

    cards.forEach(card => {
        const glaze = state.glazes.find(g => g.id === card.dataset.glazeId);
        if (!glaze) return;

        const matches = !query ||
            glaze.name?.toLowerCase().includes(lowerQuery) ||
            glaze.color?.toLowerCase().includes(lowerQuery) ||
            glaze.notes?.toLowerCase().includes(lowerQuery);

        card.style.display = matches ? 'block' : 'none';
    });
}

// =============================================================================
// IMPORT / EXPORT
// =============================================================================

function exportGlazes(format) {
    if (state.glazes.length === 0) {
        showNotification('No glazes to export', 'error');
        return;
    }

    let content, filename, type;

    if (format === 'json') {
        content = JSON.stringify(state.glazes, null, 2);
        filename = 'openglaze-export.json';
        type = 'application/json';
    } else {
        // CSV format
        const headers = ['name', 'cone', 'atmosphere', 'base_type', 'surface', 'color', 'transparency', 'notes'];
        const rows = state.glazes.map(g => headers.map(h => `"${(g[h] || '').replace(/"/g, '""')}"`).join(','));
        content = [headers.join(','), ...rows].join('\n');
        filename = 'openglaze-export.csv';
        type = 'text/csv';
    }

    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);

    showNotification(`Exported ${state.glazes.length} glazes`, 'success');
}

async function importGlazes(input) {
    const file = input.files[0];
    if (!file) return;

    try {
        const text = await file.text();
        const glazes = JSON.parse(text);

        if (!Array.isArray(glazes)) {
            throw new Error('Invalid format');
        }

        let imported = 0;
        for (const glaze of glazes) {
            try {
                const response = await fetch(`${API_BASE}/glazes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(glaze)
                });
                if (response.ok) imported++;
            } catch (e) {
                console.error('Import error for glaze:', glaze.name, e);
            }
        }

        showNotification(`Imported ${imported} glazes`, 'success');
        await loadGlazes();
    } catch (error) {
        console.error('Import error:', error);
        showNotification('Failed to import glazes. Please check the file format.', 'error');
    }

    input.value = '';
}

// =============================================================================
// SETTINGS
// =============================================================================

async function saveSettings() {
    const studioName = document.getElementById('settings-studio-name')?.value;
    const email = document.getElementById('settings-email')?.value;

    try {
        const response = await fetch(`${API_BASE}/me`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ studio_name: studioName, email })
        });

        if (response.ok) {
            showNotification('Settings saved!', 'success');
            state.user = await response.json();
        } else {
            showNotification('Failed to save settings', 'error');
        }
    } catch (error) {
        console.error('Save settings error:', error);
        showNotification('Failed to save settings', 'error');
    }
}

// =============================================================================
// TEMPLATES (Landing Page)
// =============================================================================

async function loadTemplates() {
    const container = document.getElementById('templates-list');

    if (!container) return;

    try {
        const response = await fetch(`${API_BASE}/templates`);
        const templates = await response.json();

        if (templates.length > 0) {
            container.innerHTML = templates.map(template => `
                <div class="card card-hover template-card" data-template-id="${template.id}">
                    <div class="feature-icon">${template.icon || '🎨'}</div>
                    <h3 class="feature-title">${template.name}</h3>
                    <p class="feature-description">${template.description}</p>
                    <span class="template-badge ${template.premium ? 'premium' : ''}">
                        ${template.premium ? 'Premium' : 'Free'}
                    </span>
                    <button class="btn btn-secondary btn-block" onclick="OpenGlaze.applyTemplate('${template.id}')" style="margin-top: var(--space-4);">
                        Use Template
                    </button>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load templates:', error);
        // Keep static templates as fallback
    }
}

async function applyTemplate(templateId) {
    if (!state.user) {
        window.location.href = `/auth/register?template=${templateId}`;
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/templates/${templateId}/apply`, {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(`Applied template! ${result.glazes_added} glazes added.`, 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to apply template', 'error');
        }
    } catch (error) {
        console.error('Apply template error:', error);
        showNotification('Failed to apply template', 'error');
    }
}

// =============================================================================
// BILLING
// =============================================================================

async function initiateCheckout(tier, provider = 'stripe') {
    if (!state.user) {
        window.location.href = `/auth/register?tier=${tier}`;
        return;
    }

    try {
        state.loading = true;

        const response = await fetch(`${API_BASE}/billing/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ tier, provider })
        });

        if (response.ok) {
            const result = await response.json();
            if (result.url) {
                window.location.href = result.url;
            }
        } else {
            const error = await response.json();
            showNotification(error.error || 'Checkout failed', 'error');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        showNotification('Checkout failed', 'error');
    } finally {
        state.loading = false;
    }
}

// =============================================================================
// UI HELPERS
// =============================================================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    Object.assign(notification.style, {
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        padding: '16px 24px',
        borderRadius: '12px',
        backgroundColor: type === 'success' ? 'var(--color-success)' : type === 'error' ? 'var(--color-error)' : 'var(--color-info)',
        color: 'white',
        fontWeight: '500',
        boxShadow: 'var(--shadow-lg)',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease',
        fontFamily: 'var(--font-body)'
    });

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function setupEventListeners() {
    // Handle pricing card buttons
    document.querySelectorAll('[data-tier]').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const tier = button.dataset.tier;
            initiateCheckout(tier);
        });
    });

    // Handle template selection from URL
    const urlParams = new URLSearchParams(window.location.search);
    const templateId = urlParams.get('template');
    const tier = urlParams.get('tier');

    if (templateId && state.user) {
        applyTemplate(templateId);
    }
}

// =============================================================================
// UTILITIES
// =============================================================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// CSS animation keyframes (injected)
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    .hidden {
        display: none !important;
    }
`;
document.head.appendChild(style);

// Export for global use
window.OpenGlaze = {
    checkAuth,
    applyTemplate,
    initiateCheckout,
    loadGlazes,
    createGlaze: (data) => fetch(`${API_BASE}/glazes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data)
    }).then(r => r.json()),
    deleteGlaze,
    showNotification,
    toggleTheme,
    initDashboard,
    openGlazeModal,
    closeGlazeModal,
    saveGlaze,
    editGlaze,
    duplicateGlaze,
    addIngredientRow,
    exportGlazes,
    importGlazes,
    saveSettings
};
