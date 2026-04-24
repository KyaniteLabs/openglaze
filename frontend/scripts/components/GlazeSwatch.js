/**
 * GlazeSwatch - Color swatch component for displaying glaze colors
 * Shows a circular color preview with tooltip on hover
 */
class GlazeSwatch {
    constructor(container, glaze) {
        this.container = container;
        this.glaze = glaze;
        this.element = null;
        this.render();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'glaze-swatch';
        this.element.style.backgroundColor = this.glaze.hex || '#ccc';
        this.element.title = this.glaze.name;
        this.element.dataset.glazeId = this.glaze.id || '';

        // Add tooltip on hover
        const tooltip = document.createElement('div');
        tooltip.className = 'glaze-swatch-tooltip';
        tooltip.textContent = this.glaze.name;

        this.element.appendChild(tooltip);

        // Click handler for selection
        this.element.addEventListener('click', () => {
            this.container.dispatchEvent(new CustomEvent('swatch-selected', {
                detail: { glaze: this.glaze },
                bubbles: true
            }));
        });

        this.container.appendChild(this.element);
    }

    setSelected(selected) {
        this.element.classList.toggle('selected', selected);
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

// Export for use
window.GlazeSwatch = GlazeSwatch;
