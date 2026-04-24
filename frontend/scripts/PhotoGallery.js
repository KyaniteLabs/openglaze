/**
 * PhotoGallery - Displays uploaded experiment photos in a grid with lightbox
 */
class PhotoGallery {
    constructor(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.photos = [];
        this.lightbox = null;
    }

    async load() {
        try {
            const resp = await fetch('/api/photos');
            const data = await resp.json();
            this.photos = data.photos || [];
        } catch (e) {
            this.photos = [];
        }
    }

    render() {
        this.container.innerHTML = '';

        if (this.photos.length === 0) {
            this.container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">&#128247;</div>
                    <h2>No photos yet</h2>
                    <p>Upload photos to your experiments to see them here</p>
                </div>
            `;
            return;
        }

        const grid = document.createElement('div');
        grid.className = 'photo-gallery-grid';

        this.photos.forEach(photo => {
            const item = document.createElement('div');
            item.className = 'photo-gallery-item';

            const img = document.createElement('img');
            img.className = 'photo-gallery-thumb';
            img.src = '/' + photo.photo;
            img.alt = `${photo.top_glaze} over ${photo.base_glaze}`;
            img.loading = 'lazy';

            const info = document.createElement('div');
            info.className = 'photo-gallery-info';
            info.innerHTML = `
                <div class="photo-gallery-combo">${photo.top_glaze} over ${photo.base_glaze}</div>
                ${photo.rating ? `<div class="photo-gallery-rating">${'★'.repeat(photo.rating)}${'☆'.repeat(5 - photo.rating)}</div>` : ''}
            `;

            item.appendChild(img);
            item.appendChild(info);

            item.addEventListener('click', () => this._openLightbox(photo));

            grid.appendChild(item);
        });

        this.container.appendChild(grid);
    }

    _openLightbox(photo) {
        // Remove existing lightbox
        this._closeLightbox();

        this.lightbox = document.createElement('div');
        this.lightbox.className = 'lightbox';
        this.lightbox.innerHTML = `
            <button class="lightbox-close">&times;</button>
            <img src="/${photo.photo}" alt="${photo.top_glaze} over ${photo.base_glaze}">
            <div class="lightbox-caption">${photo.top_glaze} over ${photo.base_glaze}${photo.rating ? ' — ' + '★'.repeat(photo.rating) : ''}</div>
        `;

        this.lightbox.querySelector('.lightbox-close').addEventListener('click', () => this._closeLightbox());
        this.lightbox.addEventListener('click', (e) => {
            if (e.target === this.lightbox) this._closeLightbox();
        });

        document.body.appendChild(this.lightbox);
        document.body.style.overflow = 'hidden';
    }

    _closeLightbox() {
        if (this.lightbox) {
            this.lightbox.remove();
            this.lightbox = null;
        }
        document.body.style.overflow = '';
    }

    destroy() {
        this._closeLightbox();
        if (this.container) this.container.innerHTML = '';
    }
}

window.PhotoGallery = PhotoGallery;
