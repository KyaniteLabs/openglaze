/**
 * GlazeAutocomplete - Reusable autocomplete for glaze selection
 * Shows filtered dropdown with color swatches, keyboard navigation
 */
class GlazeAutocomplete {
    constructor(container, options = {}) {
        this.container = container;
        this.glazes = options.glazes || [];
        this.placeholder = options.placeholder || 'Search glazes...';
        this.onSelect = options.onSelect || (() => {});
        this.exclude = options.exclude || [];
        this.selectedGlaze = null;
        this.activeIndex = -1;
        this.matches = [];

        this.wrapper = document.createElement('div');
        this.wrapper.className = 'autocomplete-wrapper';

        this.input = document.createElement('input');
        this.input.type = 'text';
        this.input.className = 'autocomplete-input';
        this.input.placeholder = this.placeholder;
        this.input.autocomplete = 'off';
        this.input.setAttribute('role', 'combobox');
        this.input.setAttribute('aria-autocomplete', 'list');
        this.input.setAttribute('aria-expanded', 'false');

        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.setAttribute('role', 'listbox');

        this.wrapper.appendChild(this.input);
        this.wrapper.appendChild(this.dropdown);
        this.container.appendChild(this.wrapper);

        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('focus', () => this.handleInput());
        this.input.addEventListener('blur', () => {
            setTimeout(() => this.close(), 150);
        });
    }

    filter(query) {
        if (!query || query.trim().length === 0) {
            this.matches = [];
            return;
        }

        const q = query.toLowerCase().trim();
        const excluded = new Set(this.exclude);

        this.matches = this.glazes.filter(g =>
            !excluded.has(g.name) && (
                g.name.toLowerCase().includes(q) ||
                (g.family && g.family.toLowerCase().includes(q)) ||
                (g.code && g.code.toLowerCase().includes(q))
            )
        );
    }

    highlightMatch(text, query) {
        if (!query) return text;
        const idx = text.toLowerCase().indexOf(query.toLowerCase());
        if (idx === -1) return text;
        return text.slice(0, idx) +
            '<strong class="autocomplete-highlight">' +
            text.slice(idx, idx + query.length) + '</strong>' +
            text.slice(idx + query.length);
    }

    renderItems() {
        this.dropdown.innerHTML = '';
        const query = this.input.value.trim();

        if (this.matches.length === 0) {
            if (query.length > 0) {
                this.dropdown.innerHTML = '<div class="autocomplete-empty">No glazes found</div>';
                this.dropdown.style.display = 'block';
                this.input.setAttribute('aria-expanded', 'true');
            }
            return;
        }

        this.matches.forEach((glaze, i) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item' + (i === this.activeIndex ? ' active' : '');
            item.setAttribute('role', 'option');
            item.dataset.index = i;

            const swatch = document.createElement('span');
            swatch.className = 'autocomplete-item-swatch';
            swatch.style.backgroundColor = glaze.hex || '#ccc';

            const nameEl = document.createElement('span');
            nameEl.className = 'autocomplete-item-name';
            nameEl.innerHTML = this.highlightMatch(glaze.name, query);

            item.appendChild(swatch);
            item.appendChild(nameEl);

            if (glaze.family) {
                const familyEl = document.createElement('span');
                familyEl.className = 'autocomplete-item-family';
                familyEl.textContent = glaze.family;
                item.appendChild(familyEl);
            }

            item.addEventListener('mousedown', (e) => {
                e.preventDefault();
                this.select(i);
            });

            item.addEventListener('mouseenter', () => {
                this.activeIndex = i;
                this.updateActiveItem();
            });

            this.dropdown.appendChild(item);
        });

        this.dropdown.style.display = 'block';
        this.input.setAttribute('aria-expanded', 'true');
    }

    updateActiveItem() {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        items.forEach((item, i) => {
            item.classList.toggle('active', i === this.activeIndex);
        });
    }

    handleInput() {
        this.activeIndex = -1;
        this.filter(this.input.value);
        this.renderItems();
    }

    handleKeydown(e) {
        if (this.dropdown.style.display === 'none' && e.key !== 'ArrowDown') return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (this.matches.length === 0) return;
                this.activeIndex = Math.min(this.activeIndex + 1, this.matches.length - 1);
                this.updateActiveItem();
                this.scrollActiveIntoView();
                break;

            case 'ArrowUp':
                e.preventDefault();
                if (this.activeIndex < 0) return;
                this.activeIndex = Math.max(this.activeIndex - 1, 0);
                this.updateActiveItem();
                this.scrollActiveIntoView();
                break;

            case 'Enter':
                if (this.activeIndex >= 0 && this.activeIndex < this.matches.length) {
                    e.preventDefault();
                    this.select(this.activeIndex);
                }
                break;

            case 'Escape':
                e.preventDefault();
                this.close();
                this.input.blur();
                break;
        }
    }

    scrollActiveIntoView() {
        const active = this.dropdown.querySelector('.autocomplete-item.active');
        if (active) {
            active.scrollIntoView({ block: 'nearest' });
        }
    }

    select(index) {
        const glaze = this.matches[index];
        if (!glaze) return;

        this.selectedGlaze = glaze;
        this.input.value = glaze.name;
        this.close();
        this.onSelect(glaze);
    }

    close() {
        this.dropdown.style.display = 'none';
        this.input.setAttribute('aria-expanded', 'false');
    }

    getValue() {
        return this.input.value;
    }

    getSelectedGlaze() {
        return this.selectedGlaze;
    }

    reset() {
        this.input.value = '';
        this.selectedGlaze = null;
        this.activeIndex = -1;
        this.matches = [];
        this.close();
    }

    setExclude(names) {
        this.exclude = names;
        // Re-filter if input has a value
        if (this.input.value.trim()) {
            this.handleInput();
        }
    }
}

window.GlazeAutocomplete = GlazeAutocomplete;
