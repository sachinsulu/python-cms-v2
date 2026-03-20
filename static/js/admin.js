/**
 * Python CMS v2 — Admin Panel JavaScript
 * Handles: sidebar, messages, toggle, bulk actions, drag-sort, slug check, modal
 */

"use strict";

/**
 * Global Configuration
 */
const CONFIG = {
  images: {
    maxSize: 2 * 1024 * 1024,
    allowedTypes: [
      "image/jpeg",
      "image/png",
      "image/gif",
      "image/webp",
      "image/heic",
    ],
    allowedExtensions: ["jpg", "jpeg", "png", "gif", "webp", "heic"],
  },
  limits: {
    id_meta_title: 60,
    id_meta_description: 160,
    id_meta_keywords: 205,
  },
};

// ------------------------------------------------------------------ //
// CSRF helper
// ------------------------------------------------------------------ //

function getCsrf() {
  const meta = document.querySelector("[name=csrfmiddlewaretoken]");
  if (meta) return meta.value;
  const body = document.querySelector("body");
  return body ? body.dataset.csrf : "";
}

function postJson(url, data) {
  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrf(),
    },
    body: JSON.stringify(data),
  }).then((r) => r.json());
}

function postForm(url, formData) {
  formData.append("csrfmiddlewaretoken", getCsrf());
  return fetch(url, { method: "POST", body: formData }).then((r) => r.json());
}

// ------------------------------------------------------------------ //
// Toast notifications
// ------------------------------------------------------------------ //

const toast = (() => {
  let el = null;
  let timer = null;

  function getEl() {
    if (!el) {
      el = document.createElement("div");
      el.className = "toast";
      document.body.appendChild(el);
    }
    return el;
  }

  return {
    show(msg, duration = 3000) {
      const t = getEl();
      t.textContent = msg;
      t.classList.add("show");
      clearTimeout(timer);
      timer = setTimeout(() => t.classList.remove("show"), duration);
    },
  };
})();

// ------------------------------------------------------------------ //
// Sidebar toggle
// ------------------------------------------------------------------ //

document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("sidebar-toggle");
  const shell = document.querySelector(".cms-shell");
  const sidebar = document.querySelector(".sidebar");

  if (toggle && shell) {
    toggle.addEventListener("click", () => {
      const isCollapsed = sidebar.classList.toggle("collapsed");
      shell.classList.toggle("sidebar-collapsed", isCollapsed);
      localStorage.setItem("cms_sidebar", isCollapsed ? "0" : "1");
    });

    if (localStorage.getItem("cms_sidebar") === "0") {
      sidebar.classList.add("collapsed");
      shell.classList.add("sidebar-collapsed");
    }
  }
});

// ------------------------------------------------------------------ //
// Auto-dismiss messages
// ------------------------------------------------------------------ //

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".message").forEach((msg) => {
    setTimeout(() => {
      msg.style.transition = "opacity .4s";
      msg.style.opacity = "0";
      setTimeout(() => msg.remove(), 400);
    }, 4000);
  });
});

// ------------------------------------------------------------------ //
// Toggle status (AJAX)
// ------------------------------------------------------------------ //

function initToggles() {
  // Use event delegation so toggles re-added by DataTables drawCallback work
  document.querySelectorAll("[data-toggle-url]").forEach((wrap) => {
    // Avoid double-binding by checking for a flag
    if (wrap.dataset.toggleBound) return;
    wrap.dataset.toggleBound = "1";

    wrap.addEventListener("click", async () => {
      const url = wrap.dataset.toggleUrl;
      const sw = wrap.querySelector(".toggle-switch");
      try {
        const res = await postJson(url, {});
        if (res.status !== undefined) {
          sw.classList.toggle("on", res.status);
          toast.show(res.message || "Status updated");
        }
      } catch (e) {
        toast.show("Error updating status");
      }
    });
  });
}

// ------------------------------------------------------------------ //
// Delete modal
// ------------------------------------------------------------------ //

function openDeleteModal(url, label) {
  const overlay = document.getElementById("delete-modal");
  const text = document.getElementById("delete-modal-text");
  const form = document.getElementById("delete-form");

  if (!overlay) return;

  text.textContent = label
    ? `Are you sure you want to delete "${label}"? This cannot be undone.`
    : "Are you sure? This cannot be undone.";

  form.action = url;
  overlay.classList.add("open");
}

function closeDeleteModal() {
  const overlay = document.getElementById("delete-modal");
  if (overlay) overlay.classList.remove("open");
}

document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("delete-modal");
  if (overlay) {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeDeleteModal();
    });
  }
});

// ------------------------------------------------------------------ //
// Bulk actions
// ------------------------------------------------------------------ //

function initBulk() {
  const selectAll = document.getElementById("select-all");
  if (!selectAll) return;

  selectAll.addEventListener("change", () => {
    document.querySelectorAll(".row-checkbox").forEach((cb) => {
      cb.checked = selectAll.checked;
    });
  });
}

async function bulkAction(modelKey, action) {
  const checked = [...document.querySelectorAll(".row-checkbox:checked")];
  if (!checked.length) {
    toast.show("No items selected");
    return;
  }

  if (action === "delete") {
    openDeleteModal(null, `${checked.length} selected item(s)`);
    const form = document.getElementById("delete-form");
    form.onsubmit = async (e) => {
      e.preventDefault();
      closeDeleteModal();
      await executeBulkAction(modelKey, "delete", checked);
    };
    return;
  }

  await executeBulkAction(modelKey, action, checked);
}

async function executeBulkAction(modelKey, action, checked) {
  const fd = new FormData();
  fd.append("action", action);
  checked.forEach((cb) => fd.append("selected_ids", cb.value));

  try {
    const res = await postForm(`/apanel/core/bulk/${modelKey}/`, fd);
    if (res.success) {
      toast.show(res.message);
      setTimeout(() => location.reload(), 800);
    } else {
      toast.show(res.error || "Action failed");
    }
  } catch (e) {
    toast.show("Server error");
  }
}

// ------------------------------------------------------------------ //
// DataTables — initialise all .cms-table elements
// ------------------------------------------------------------------ //

// Holds the DataTables API instance for each table, keyed by the table element.
// We need this so initSortable can tell DataTables about row reorders.
const _dtInstances = new WeakMap();

function initAllDataTables() {
  const dtConstructor =
    window.DataTable || (window.jQuery && window.jQuery.fn.DataTable);
  if (!dtConstructor) {
    console.warn("CMS: DataTables not loaded (constructor not found).");
    return;
  }

  document.querySelectorAll(".cms-table").forEach((tableEl) => {
    if (_dtInstances.has(tableEl) || tableEl.classList.contains("no-datatable"))
      return;

    const isSortable = !!tableEl.querySelector("tbody[data-sortable]");

    try {
      // Use jQuery constructor if available, otherwise window.DataTable
      const $table = window.jQuery ? window.jQuery(tableEl) : null;

      const options = {
        pageLength: 20,
        lengthMenu: [10, 20, 50, 100],
        order: [],
        columnDefs: [
          { targets: 0, orderable: false },
          { targets: 1, orderable: false },
          { targets: "no-sort", orderable: false },
          { targets: -1, orderable: !isSortable },
        ],
        language: {
          search: "",
          searchPlaceholder: "Search...",
          info: "_START_–_END_ of _TOTAL_",
          infoEmpty: "0 items",
          paginate: {
            previous: "‹",
            next: "›",
          },
        },
        layout: {
          topStart: "pageLength",
          topEnd: "search",
          bottomStart: "",
          bottomEnd: "paging",
        },
        drawCallback: function () {
          initToggles();
        },
      };

      const dtInstance = $table
        ? $table.DataTable(options)
        : new dtConstructor(tableEl, options);

      // store the instance
      _dtInstances.set(tableEl, dtInstance);
    } catch (err) {
      console.error("CMS: DataTable init error on", tableEl, err);
    }
  });

  // style search inputs
  document.querySelectorAll(".dt-search input").forEach((input) => {
    input.classList.add("form-control");
  });
}

// ------------------------------------------------------------------ //
// Drag-and-drop sorting (SortableJS)
//
// KEY RULE: SortableJS moves rows in the real DOM.
// DataTables keeps its own internal row index.
// After every drag, we must call dt.row.add / invalidate so the two
// stay in sync — otherwise paging and search break after a sort.
//
// The simplest correct approach: after saving the order to the server,
// reload the page. This guarantees DataTables, SortableJS, and the DB
// are all in sync without complex row-swap bookkeeping.
// ------------------------------------------------------------------ //

function initSortable(modelKey) {
  const tbody = document.querySelector("tbody[data-sortable]");
  if (!tbody || typeof Sortable === "undefined") return;

  Sortable.create(tbody, {
    handle: ".drag-handle",
    animation: 150,
    ghostClass: "sortable-ghost",

    onEnd: async () => {
      // Collect the new order from the DOM (what SortableJS just produced)
      const order = [...tbody.querySelectorAll("tr[data-id]")].map(
        (r) => r.dataset.id,
      );

      try {
        const res = await postJson(`/apanel/core/sort/${modelKey}/`, { order });
        if (res.success) {
          toast.show("Order saved");
          // Reload so DataTables re-initialises with the new server order.
          // Without this, DataTables internal index is out of sync with the DOM
          // and paging/search will show rows in the wrong order.
          setTimeout(() => location.reload(), 600);
        } else {
          toast.show("Failed to save order");
        }
      } catch (e) {
        toast.show("Failed to save order");
      }
    },
  });
}

// ------------------------------------------------------------------ //
// Image preview & validation
// ------------------------------------------------------------------ //

function initImagePreview() {
  const imageFields = ["image", "banner_image", "avatar"];

  imageFields.forEach((fieldName) => {
    const imageInput = document.querySelector(
      `input[type="file"][name="${fieldName}"]`,
    );
    if (!imageInput) return;

    // Skip fields managed by MediaPickerWidget
    if (imageInput.closest(".media-picker")) return;

    let previewId = fieldName + "Preview";
    let imagePreview = document.getElementById(previewId);

    if (!imagePreview) {
      imagePreview = document.createElement("div");
      imagePreview.id = previewId;
      imageInput.parentNode.insertBefore(imagePreview, imageInput.nextSibling);
    }

    imageInput.addEventListener("change", () => {
      const file = imageInput.files[0];
      if (!file) return;

      if (file.size > CONFIG.images.maxSize) {
        toast.show("Image too large — max 2 MB");
        imageInput.value = "";
        return;
      }

      const ext = file.name.split(".").pop().toLowerCase();
      if (!CONFIG.images.allowedExtensions.includes(ext)) {
        toast.show(`Invalid file type .${ext}`);
        imageInput.value = "";
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        imagePreview.innerHTML = `<img src="${e.target.result}"
          style="max-width:200px; max-height:140px; margin-top:8px;
                 border-radius:6px; border:1px solid var(--border);">`;
      };
      reader.readAsDataURL(file);
    });
  });
}

// ------------------------------------------------------------------ //
// SEO fields toggle
// ------------------------------------------------------------------ //

function initSEOToggle() {
  const toggle = document.getElementById("seo-toggle");
  const panel = document.getElementById("seo-panel");
  if (!toggle || !panel) return;

  toggle.addEventListener("click", () => {
    const open = panel.style.display !== "none";
    panel.style.display = open ? "none" : "block";
    toggle.textContent = open ? "▸ SEO / Meta" : "▾ SEO / Meta";
  });
}

// ------------------------------------------------------------------ //
// Slug availability check
// ------------------------------------------------------------------ //

function initSlugCheck(modelName, objectId) {
  const slugInput = document.getElementById("id_slug");
  const titleInput = document.getElementById("id_title");
  const slugMessage = document.getElementById("slug-status");
  if (!slugInput) return;

  let debounceTimer;
  let slugManuallyEdited = false;

  function slugify(text) {
    return text
      .toString()
      .toLowerCase()
      .trim()
      .replace(/\s+/g, "-")
      .replace(/[^\w\-]+/g, "")
      .replace(/--+/g, "-")
      .replace(/^-+/, "")
      .replace(/-+$/, "")
      .substring(0, 80);
  }

  function checkSlug(slug) {
    if (!slug) {
      if (slugMessage) {
        slugMessage.textContent = "";
      }
      return;
    }
    const params = new URLSearchParams({ slug });
    if (objectId) params.append("exclude_id", objectId);

    fetch(`/apanel/core/slug/${modelName}/?${params}`)
      .then((r) => r.json())
      .then((data) => {
        if (!slugMessage) return;
        if (data.error) {
          slugMessage.textContent = `⚠ ${data.error}`;
          slugMessage.style.color = "#f59e0b";
        } else if (!data.available) {
          slugMessage.textContent = "✗ Slug already in use";
          slugMessage.style.color = "#dc2626";
        } else {
          slugMessage.textContent = "✓ Available";
          slugMessage.style.color = "#16a34a";
        }
      })
      .catch(() => {});
  }

  slugInput.addEventListener("input", () => {
    slugManuallyEdited = true;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => checkSlug(slugInput.value.trim()), 400);
  });

  if (titleInput) {
    titleInput.addEventListener("input", () => {
      if (slugManuallyEdited) return;
      slugInput.value = slugify(titleInput.value);
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => checkSlug(slugInput.value), 400);
    });
  }

  slugInput.addEventListener("blur", () => checkSlug(slugInput.value.trim()));
}

// ------------------------------------------------------------------ //
// Character counters for SEO fields
// ------------------------------------------------------------------ //

function initCharCounters() {
  Object.keys(CONFIG.limits).forEach((fieldId) => {
    const input = document.getElementById(fieldId);
    if (!input) return;

    let counterId = fieldId + "-counter";
    let counter = document.getElementById(counterId);
    if (!counter) {
      counter = document.createElement("div");
      counter.id = counterId;
      counter.style.cssText = "font-size:12px; margin-top:4px;";
      input.parentNode.insertBefore(counter, input.nextSibling);
    }

    const max = CONFIG.limits[fieldId];
    const min = fieldId === "id_meta_title" ? 20 : 0;

    function update() {
      const len = input.value.length;
      const remaining = max - len;

      if (len > max) {
        input.value = input.value.substring(0, max);
        counter.textContent = "Limit reached";
        counter.style.color = "#dc2626";
        return;
      }
      if (min && len > 0 && len < min) {
        counter.textContent = `At least ${min} characters required`;
        counter.style.color = "#dc2626";
      } else if (remaining === 0) {
        counter.textContent = "Limit reached";
        counter.style.color = "#dc2626";
      } else if (remaining <= 10) {
        counter.textContent = `${remaining} characters remaining`;
        counter.style.color = "#f59e0b";
      } else {
        counter.textContent = `${remaining} characters remaining`;
        counter.style.color = "#6b7280";
      }
    }

    input.addEventListener("input", update);
    update();
  });
}

// ------------------------------------------------------------------ //
// Bootstrap — run everything on DOMContentLoaded
// ------------------------------------------------------------------ //

window.addEventListener("load", () => {
  initToggles();
  initBulk();
  initImagePreview();
  initSEOToggle();
  initAllDataTables();
  initCharCounters();
});
