/**
 * Python CMS v2 — Admin Panel JavaScript
 * Handles: sidebar, messages, toggle, bulk actions, drag-sort, slug check, modal
 */

'use strict';

/**
 * Global Configuration
 */
const CONFIG = {
  images: {
    maxSize: 2 * 1024 * 1024, // 2MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic'],
    allowedExtensions: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic']
  },
  limits: {
    'id_meta_title': 60,
    'id_meta_description': 160,
    'id_meta_keywords': 205
  }
};

// ------------------------------------------------------------------ //
// CSRF helper
// ------------------------------------------------------------------ //

function getCsrf() {
  const meta = document.querySelector('[name=csrfmiddlewaretoken]');
  if (meta) return meta.value;
  const body = document.querySelector('body');
  return body ? body.dataset.csrf : '';
}

function postJson(url, data) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrf(),
    },
    body: JSON.stringify(data),
  }).then(r => r.json());
}

function postForm(url, formData) {
  formData.append('csrfmiddlewaretoken', getCsrf());
  return fetch(url, { method: 'POST', body: formData }).then(r => r.json());
}

// ------------------------------------------------------------------ //
// Toast notifications
// ------------------------------------------------------------------ //

const toast = (() => {
  let el = null;
  let timer = null;

  function getEl() {
    if (!el) {
      el = document.createElement('div');
      el.className = 'toast';
      document.body.appendChild(el);
    }
    return el;
  }

  return {
    show(msg, duration = 3000) {
      const t = getEl();
      t.textContent = msg;
      t.classList.add('show');
      clearTimeout(timer);
      timer = setTimeout(() => t.classList.remove('show'), duration);
    }
  };
})();

// ------------------------------------------------------------------ //
// Sidebar toggle
// ------------------------------------------------------------------ //

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('sidebar-toggle');
  const shell = document.querySelector('.cms-shell');
  const sidebar = document.querySelector('.sidebar');

  if (toggle && shell) {
    toggle.addEventListener('click', () => {
      const isCollapsed = sidebar.classList.toggle('collapsed');
      shell.classList.toggle('sidebar-collapsed', isCollapsed);
      localStorage.setItem('cms_sidebar', isCollapsed ? '0' : '1');
    });

    // Restore state
    if (localStorage.getItem('cms_sidebar') === '0') {
      sidebar.classList.add('collapsed');
      shell.classList.add('sidebar-collapsed');
    }
  }
});

// ------------------------------------------------------------------ //
// Auto-dismiss messages
// ------------------------------------------------------------------ //

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.message').forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity .4s';
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 400);
    }, 4000);
  });
});

// ------------------------------------------------------------------ //
// Toggle status (AJAX)
// ------------------------------------------------------------------ //

function initToggles() {
  document.querySelectorAll('[data-toggle-url]').forEach(wrap => {
    wrap.addEventListener('click', async () => {
      const url = wrap.dataset.toggleUrl;
      const sw = wrap.querySelector('.toggle-switch');

      try {
        const res = await postJson(url, {});
        if (res.status !== undefined) {
          sw.classList.toggle('on', res.status);
          toast.show(res.message || 'Status updated');
        }
      } catch (e) {
        toast.show('Error updating status');
      }
    });
  });
}

// ------------------------------------------------------------------ //
// Delete modal
// ------------------------------------------------------------------ //

let pendingDeleteForm = null;

function openDeleteModal(url, label) {
  const overlay = document.getElementById('delete-modal');
  const text = document.getElementById('delete-modal-text');
  const form = document.getElementById('delete-form');

  if (!overlay) return;

  text.textContent = label
    ? `Are you sure you want to delete "${label}"? This cannot be undone.`
    : 'Are you sure? This cannot be undone.';

  form.action = url;
  overlay.classList.add('open');

  // Handle submission via AJAX
  form.onsubmit = async (e) => {
    e.preventDefault();
    closeDeleteModal();

    // If no URL (bulk delete), bulkAction handles it
    if (!url) return;

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() }
      }).then(r => r.json());

      if (res.success) {
        toast.show(res.message || 'Deleted successfully');
        setTimeout(() => location.reload(), 500);
      } else {
        toast.show(res.error || 'Delete failed');
      }
    } catch (err) {
      toast.show('Server error during deletion');
    }
  };
}

function closeDeleteModal() {
  const overlay = document.getElementById('delete-modal');
  if (overlay) overlay.classList.remove('open');
}

// Close on overlay click
document.addEventListener('click', e => {
  const overlay = document.getElementById('delete-modal');
  if (overlay && e.target === overlay) closeDeleteModal();
});

// ------------------------------------------------------------------ //
// Bulk actions
// ------------------------------------------------------------------ //

function initBulk() {
  const selectAll = document.getElementById('select-all');
  if (!selectAll) return;

  const checkboxes = () => document.querySelectorAll('.row-checkbox');

  selectAll.addEventListener('change', () => {
    checkboxes().forEach(cb => { cb.checked = selectAll.checked; });
  });

  // Keep select-all in sync
  document.addEventListener('change', e => {
    if (e.target.classList.contains('row-checkbox')) {
      const all = checkboxes();
      const checked = document.querySelectorAll('.row-checkbox:checked');
      selectAll.indeterminate = checked.length > 0 && checked.length < all.length;
      selectAll.checked = checked.length === all.length;
    }
  });
}

async function bulkAction(modelKey, action) {
  const checked = document.querySelectorAll('.row-checkbox:checked');
  if (!checked.length) { toast.show('No items selected.'); return; }

  if (action === 'delete') {
    openDeleteModal(null, `${checked.length} selected item(s)`);
    // Override the form to submit bulk delete
    const form = document.getElementById('delete-form');
    form.onsubmit = async (e) => {
      e.preventDefault();
      closeDeleteModal();
      await executeBulkAction(modelKey, 'delete', checked);
    };
    return;
  }

  await executeBulkAction(modelKey, action, checked);
}

async function executeBulkAction(modelKey, action, checked) {
  const fd = new FormData();
  fd.append('action', action);
  checked.forEach(cb => fd.append('selected_ids', cb.value));

  try {
    const res = await postForm(`/core/bulk/${modelKey}/`, fd);
    if (res.success) {
      toast.show(res.message);
      setTimeout(() => location.reload(), 800);
    } else {
      toast.show(res.error || 'Action failed');
    }
  } catch (e) {
    toast.show('Server error');
  }
}

// ------------------------------------------------------------------ //
// Drag-and-drop sorting (SortableJS)
// ------------------------------------------------------------------ //

function initSortable(modelKey) {
  const tbody = document.querySelector('tbody[data-sortable]');
  if (!tbody || typeof Sortable === 'undefined') return;

  Sortable.create(tbody, {
    handle: '.drag-handle',
    animation: 150,
    ghostClass: 'sortable-ghost',
    onEnd: async () => {
      const order = [...tbody.querySelectorAll('tr[data-id]')].map(r => r.dataset.id);
      try {
        const res = await postJson(`/core/sort/${modelKey}/`, { order });
        if (res.success) toast.show('Order saved');
      } catch (e) {
        toast.show('Failed to save order');
      }
    },
  });
}

// ------------------------------------------------------------------ //
// Global DataTables Initialization
// ------------------------------------------------------------------ //

function initAllDataTables() {
  if (typeof DataTable === 'undefined') return;

  const tables = document.querySelectorAll('.cms-table');

  tables.forEach(tableEl => {
    if (DataTable.isDataTable(tableEl) || tableEl.classList.contains('no-datatable')) return;

    const isSortable = !!tableEl.querySelector('tbody[data-sortable]');

    try {
      new DataTable(tableEl, {
        pageLength: 20,
        lengthMenu: [10, 20, 50, 100],
        order: [],
        // ✅ Split into separate entries — overlapping targets in a single
        //    entry causes DataTables 2.x to throw "Cannot read properties
        //    of undefined (reading 'apply')" internally.
        columnDefs: [
          { targets: 'no-sort', orderable: false },  // any <th class="no-sort">
          { targets: 0, orderable: false },           // drag handle col
          { targets: 1, orderable: false },           // checkbox col
          { targets: -1, orderable: !isSortable },    // actions col: lock when drag-sort is active
        ],
        language: {
          search: "",
          searchPlaceholder: "Search...",
        },
        layout: {
          topStart: 'search',
          topEnd: 'paging',
          bottomStart: 'info',
          bottomEnd: 'lengthMenu'
        },
        drawCallback: function () {
          initToggles();
        }
      });
    } catch (e) {
      console.error('CMS: Error initializing DataTable:', e);
    }
  });

  // Re-style search inputs
  document.querySelectorAll('.dt-search input').forEach(input => {
    if (!input.classList.contains('form-control')) {
      input.classList.add('form-control');
    }
  });
}

// ------------------------------------------------------------------ //
// Image preview & validation
// ------------------------------------------------------------------ //

function initImagePreview() {
  const imageFields = ['image', 'banner_image', 'avatar'];

  imageFields.forEach(fieldName => {
    const imageInput = document.querySelector(`input[type="file"][name="${fieldName}"]`);
    if (!imageInput) return;

    // Skip fields managed by MediaPickerWidget (handled by media-picker.js)
    if (imageInput.closest('.media-picker')) return;

    let previewId = fieldName + 'Preview';
    let imagePreview = document.getElementById(previewId);

    // If preview container doesn't exist, create it dynamically
    if (!imagePreview) {
      imagePreview = document.createElement('div');
      imagePreview.id = previewId;
      // Insert it right after the input field
      imageInput.parentNode.insertBefore(imagePreview, imageInput.nextSibling);
    }

    const removeInput = document.getElementById(`remove_${fieldName}`); // Optional
    const imageLabel = imageInput.previousElementSibling;

    // Django's ClearableFileInput might currently show an existing link
    const existingImageLink = imageInput.parentNode.querySelector('a[href*="/media/"]');
    let existingImageUrl = existingImageLink ? existingImageLink.href : null;

    // Optional: Django specific clear checkbox
    const clearCheckId = fieldName + '-clear_id';
    const clearCheck = document.getElementById(clearCheckId) || document.querySelector(`input[name="${fieldName}-clear"]`);

    function toggleInputVisibility(show) {
      if (show) {
        imageInput.style.opacity = '1';
        imageInput.style.height = 'auto';
        imageInput.style.position = 'relative';
        if (clearCheck) clearCheck.style.display = 'inline-block';
      } else {
        imageInput.style.opacity = '0';
        imageInput.style.height = '0';
        imageInput.style.position = 'absolute';
        if (clearCheck) clearCheck.style.display = 'none';
      }
    }

    function renderPreview(src, isExisting = false) {
      const labelName = fieldName.replace('_', ' ');
      const label = isExisting ? `Current ${labelName}` : `New ${labelName} selected`;

      // Clean up the default django "Currently: " and "Change: " elements
      if (existingImageLink) {
        existingImageLink.style.display = 'none';
        const parent = imageInput.parentNode;
        Array.from(parent.childNodes).forEach(node => {
          if (node.nodeType === Node.TEXT_NODE) {
            node.textContent = ''; // wipe text like "Currently:" and "Change:"
          }
          if (node.tagName === 'BR') {
            node.style.display = 'none';
          }
          if (node.tagName === 'LABEL' && node.getAttribute('for') === clearCheckId) {
            node.style.display = 'none';
          }
        });
      }

      imagePreview.innerHTML = `
                <div class="preview-wrapper" style="position:relative; display:inline-block; margin-top: 10px;">
                    <img src="${src}" style="max-width:300px; max-height:200px; border:1px solid #e5e7eb; border-radius:4px; display: block;">
                    <span class="remove-image" style="position:absolute; top:-8px; right:-8px; background:#ef4444; color:white; border-radius:50%; width:24px; height:24px; text-align:center; line-height:24px; cursor:pointer; font-weight:bold; font-size: 16px;">×</span>
                    <p style="margin-top: 5px; font-size: 12px; color: #666;">${label}</p>
                </div>`;
      toggleInputVisibility(false);
    }

    // Event: Remove Image
    imagePreview.addEventListener('click', function (e) {
      if (e.target.closest('.remove-image')) {
        const labelName = fieldName.replace('_', ' ');
        e.preventDefault();

        // If there's a django clear checkbox, check it so it deletes on backend
        if (clearCheck) clearCheck.checked = true;

        if (removeInput) removeInput.value = '1';
        imagePreview.innerHTML = `<p class="no-image text-muted" style="margin-top:8px; font-size:13px;">No ${labelName} selected</p>`;
        imageInput.value = '';
        toggleInputVisibility(true);
      }
    });

    // Event: Upload New Image
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) {
        // They canceled the file browser window
        imagePreview.innerHTML = '';
        toggleInputVisibility(true);
        return;
      }

      if (file.size > CONFIG.images.maxSize) {
        toast.show(`File too large! Max 2MB.`);
        this.value = '';
        return;
      }
      if (!CONFIG.images.allowedTypes.includes(file.type)) {
        toast.show('Invalid file type! Allowed: JPG, PNG, GIF, WebP');
        this.value = '';
        return;
      }

      if (removeInput) removeInput.value = '0';
      if (clearCheck) clearCheck.checked = false; // uncheck delete if they uploaded new

      const reader = new FileReader();
      reader.onload = (e) => renderPreview(e.target.result, false);
      reader.readAsDataURL(file);
    });

    if (existingImageUrl) {
      renderPreview(existingImageUrl, true);
    }
  });
}

// ------------------------------------------------------------------ //
// SEO Meta Panel Toggle
// ------------------------------------------------------------------ //

function initSEOToggle() {
  const toggleBtn = document.getElementById('toggleMeta');
  const metaContent = document.getElementById('metaContent');
  const statusIcon = document.getElementById('metaStatusIcon');

  if (!toggleBtn || !metaContent || !statusIcon) return;

  const metaInputs = metaContent.querySelectorAll('input, textarea');
  const form = document.querySelector('form#cms-form');

  toggleBtn.addEventListener('click', function () {
    const isHidden = metaContent.style.display === "none";
    metaContent.style.display = isHidden ? "block" : "none";
    statusIcon.textContent = isHidden ? "▲" : "▼";

    // Toggle Required Attributes (so they are strictly required only when the panel is shown)
    metaInputs.forEach(input => {
      if (isHidden) input.setAttribute('required', 'required');
      else {
        input.removeAttribute('required');
        input.classList.remove('input-error');
      }
    });
  });

  if (form) {
    form.addEventListener('submit', function (e) {
      // Only validate if they opened the panel
      if (metaContent.style.display === "none") return;

      let invalid = false;
      metaInputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
          input.classList.add('input-error');
          invalid = true;
        } else {
          input.classList.remove('input-error');
        }
      });

      if (invalid) {
        e.preventDefault();
        toast.show("Please fill out all visible SEO / Meta fields.", "error");
      }
    });
  }
}

// ------------------------------------------------------------------ //
// Init on DOM ready
// ------------------------------------------------------------------ //

document.addEventListener('DOMContentLoaded', () => {
  initToggles();
  initBulk();
  initImagePreview();
  initSEOToggle();
  initAllDataTables();

  // Character Counters
  Object.keys(CONFIG.limits).forEach(fieldId => {
    const inputField = document.getElementById(fieldId);
    if (!inputField) return;

    // Create counter container if not exists dynamically
    let counterId = fieldId + '-counter';
    let counter = document.getElementById(counterId);
    if (!counter) {
      counter = document.createElement('div');
      counter.id = counterId;
      counter.style.fontSize = '12px';
      counter.style.marginTop = '4px';
      inputField.parentNode.insertBefore(counter, inputField.nextSibling);
    }

    let maxChars = CONFIG.limits[fieldId];
    let minChars = fieldId === 'id_meta_title' ? 20 : 0;

    function updateCounter() {
      let currentLength = inputField.value.length;
      let remaining = maxChars - currentLength;

      if (currentLength > maxChars) {
        inputField.value = inputField.value.substring(0, maxChars);
        counter.textContent = "Limit reached";
        counter.style.color = "#dc2626";
        return;
      }

      if (fieldId === 'id_meta_title' && currentLength > 0 && currentLength < minChars) {
        counter.textContent = "More than 20 characters required";
        counter.style.color = "#dc2626";
      } else if (remaining === 0) {
        counter.textContent = "Limit reached";
        counter.style.color = "#dc2626";
      } else if (remaining <= 10) {
        counter.textContent = remaining + " characters remaining";
        counter.style.color = "#f59e0b";
      } else {
        counter.textContent = remaining + " characters remaining";
        counter.style.color = "#6b7280";
      }
    }

    inputField.addEventListener("input", updateCounter);
    updateCounter(); // init on load
  });
});