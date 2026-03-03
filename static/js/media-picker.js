/**
 * Media Picker — JavaScript
 * Handles: Library modal, upload, select, remove for MediaPickerWidget
 */
'use strict';

(function () {

    // ------------------------------------------------------------------ //
    // Shared modal (singleton — one modal for all pickers on the page)
    // ------------------------------------------------------------------ //

    let modal = null;
    let activePicker = null;  // which picker initiated the modal
    let selectedAsset = null; // currently highlighted asset in modal

    function getCSRF() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    }

    function ensureModal() {
        if (modal) return modal;

        const overlay = document.createElement('div');
        overlay.className = 'media-modal-overlay';
        overlay.id = 'media-library-modal';
        overlay.innerHTML = `
            <div class="media-modal">
                <div class="media-modal-header">
                    <h3><i class="fa-solid fa-images" style="margin-right:6px;"></i>Media Library</h3>
                    <button type="button" class="media-modal-close">&times;</button>
                </div>
                <div class="media-modal-toolbar">
                    <button type="button" class="btn btn-primary btn-sm media-modal-upload-btn">
                        <i class="fa-solid fa-upload"></i> Upload
                    </button>
                    <input type="file" class="media-modal-file-input" accept="image/*" style="display:none;">
                    <span class="media-modal-upload-status" style="font-size:12px; color:#6b7280;"></span>
                </div>
                <div class="media-modal-body">
                    <div class="media-modal-loading">Loading library</div>
                </div>
                <div class="media-modal-footer">
                    <button type="button" class="btn btn-secondary btn-sm media-modal-cancel-btn">Cancel</button>
                    <button type="button" class="btn btn-primary btn-sm media-modal-select-btn" disabled>Select</button>
                </div>
            </div>`;

        document.body.appendChild(overlay);
        modal = overlay;

        // Event: close
        overlay.querySelector('.media-modal-close').addEventListener('click', closeModal);
        overlay.querySelector('.media-modal-cancel-btn').addEventListener('click', closeModal);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });

        // Event: upload button
        const uploadBtn = overlay.querySelector('.media-modal-upload-btn');
        const fileInput = overlay.querySelector('.media-modal-file-input');
        const statusEl = overlay.querySelector('.media-modal-upload-status');

        uploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async () => {
            const file = fileInput.files[0];
            if (!file) return;

            statusEl.textContent = 'Uploading…';
            uploadBtn.disabled = true;

            const fd = new FormData();
            fd.append('file', file);
            fd.append('csrfmiddlewaretoken', getCSRF());

            try {
                const res = await fetch('/media/upload/', {
                    method: 'POST',
                    body: fd,
                });
                const data = await res.json();

                if (data.error) {
                    statusEl.textContent = `Error: ${data.error}`;
                } else {
                    statusEl.textContent = 'Uploaded!';
                    // Reload library grid
                    await loadLibrary();
                    // Auto-select the new asset
                    setTimeout(() => {
                        const item = modal.querySelector(`[data-asset-id="${data.id}"]`);
                        if (item) {
                            item.click();
                        }
                    }, 50);
                }
            } catch (e) {
                statusEl.textContent = 'Upload failed';
            }

            uploadBtn.disabled = false;
            fileInput.value = '';
        });

        // Event: select button
        overlay.querySelector('.media-modal-select-btn').addEventListener('click', () => {
            if (selectedAsset && activePicker) {
                applySelection(activePicker, selectedAsset);
                closeModal();
            }
        });

        return modal;
    }

    function openModal(picker) {
        activePicker = picker;
        selectedAsset = null;
        const m = ensureModal();
        m.querySelector('.media-modal-select-btn').disabled = true;
        m.querySelector('.media-modal-upload-status').textContent = '';
        m.classList.add('open');
        loadLibrary();
    }

    function closeModal() {
        if (modal) modal.classList.remove('open');
        activePicker = null;
        selectedAsset = null;
    }

    async function loadLibrary() {
        const body = modal.querySelector('.media-modal-body');
        body.innerHTML = '<div class="media-modal-loading">Loading library</div>';

        try {
            const res = await fetch('/media/library/?type=image');
            const data = await res.json();
            body.innerHTML = data.html;

            // Wire up click handlers on items
            body.querySelectorAll('.media-library-item').forEach(item => {
                item.addEventListener('click', () => {
                    body.querySelectorAll('.media-library-item').forEach(i => i.classList.remove('selected'));
                    item.classList.add('selected');
                    selectedAsset = {
                        id: item.dataset.assetId,
                        url: item.dataset.assetUrl,
                        thumb: item.dataset.assetThumb,
                        alt: item.dataset.assetAlt,
                        name: item.dataset.assetName,
                    };
                    modal.querySelector('.media-modal-select-btn').disabled = false;
                });

                // Double-click to select immediately
                item.addEventListener('dblclick', () => {
                    item.click();
                    if (selectedAsset && activePicker) {
                        applySelection(activePicker, selectedAsset);
                        closeModal();
                    }
                });
            });
        } catch (e) {
            body.innerHTML = '<p style="color:#ef4444; text-align:center;">Failed to load library.</p>';
        }
    }

    // ------------------------------------------------------------------ //
    // Apply selection / remove — update hidden input + preview
    // ------------------------------------------------------------------ //

    function applySelection(picker, asset) {
        const hiddenInput = picker.querySelector('input[type="hidden"]');
        const preview = picker.querySelector('.media-picker-preview');

        hiddenInput.value = asset.id;
        preview.innerHTML = `
            <div class="media-picker-thumb-wrap">
                <img src="${asset.thumb}" alt="${asset.alt}">
                <span class="media-picker-remove" title="Remove">&times;</span>
                <p class="media-picker-filename">${asset.name}</p>
            </div>`;
    }

    function clearSelection(picker) {
        const hiddenInput = picker.querySelector('input[type="hidden"]');
        const preview = picker.querySelector('.media-picker-preview');

        hiddenInput.value = '';
        preview.innerHTML = '<p class="media-picker-empty">No image selected</p>';
    }

    // ------------------------------------------------------------------ //
    // Direct upload (from picker, without opening library)
    // ------------------------------------------------------------------ //

    async function directUpload(picker, file) {
        const fd = new FormData();
        fd.append('file', file);
        fd.append('csrfmiddlewaretoken', getCSRF());

        try {
            const res = await fetch('/media/upload/', {
                method: 'POST',
                body: fd,
            });
            const data = await res.json();

            if (data.error) {
                if (typeof toast !== 'undefined') toast.show(`Upload error: ${data.error}`);
                return;
            }

            applySelection(picker, {
                id: data.id,
                url: data.url,
                thumb: data.thumbnail_url,
                alt: data.alt_text,
                name: data.filename,
            });
        } catch (e) {
            if (typeof toast !== 'undefined') toast.show('Upload failed');
        }
    }

    // ------------------------------------------------------------------ //
    // Init: wire up all media pickers on the page
    // ------------------------------------------------------------------ //

    function initMediaPickers() {
        document.querySelectorAll('.media-picker').forEach(picker => {
            if (picker.dataset.initialized) return;
            picker.dataset.initialized = 'true';

            // Library button
            const libBtn = picker.querySelector('.media-picker-library-btn');
            if (libBtn) {
                libBtn.addEventListener('click', () => openModal(picker));
            }

            // Upload button
            const uploadBtn = picker.querySelector('.media-picker-upload-btn');
            const fileInput = picker.querySelector('.media-picker-file-input');
            if (uploadBtn && fileInput) {
                uploadBtn.addEventListener('click', () => fileInput.click());
                fileInput.addEventListener('change', () => {
                    const file = fileInput.files[0];
                    if (file) directUpload(picker, file);
                    fileInput.value = '';
                });
            }

            // Remove button (delegated)
            const preview = picker.querySelector('.media-picker-preview');
            if (preview) {
                preview.addEventListener('click', (e) => {
                    if (e.target.closest('.media-picker-remove')) {
                        e.preventDefault();
                        clearSelection(picker);
                    }
                });
            }
        });
    }

    // Run on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', initMediaPickers);

})();
