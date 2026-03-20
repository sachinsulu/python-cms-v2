# Python CMS v2

A production-grade Django CMS rebuilt from scratch with proper architecture.

## Architecture Highlights

- **`BaseContentModel`** — single abstract base for all content types, composed from mixins: `TimestampMixin`, `ActiveMixin`, `SortableMixin`, `SlugMixin`, `SEOMixin`.
- **`SimpleContentModel`** — lightweight base for models that don't need slugs or SEO (timestamps + active + position only).
- **`GlobalSlug`** — single DB table enforcing slug uniqueness across all content types simultaneously. Protected at three layers: form (`SlugUniqueMixin`), save (`update_or_create`), and DB (PK constraint).
- **Registry pattern** — apps self-register via `AppConfig.ready()`. Adding a new content type requires zero changes to shared code.
- **Generic CRUD views** — `ContentListView`, `ContentCreateView`, `ContentUpdateView`. Each app subclasses these with a few class attributes.
- **Auto-wired REST API** — a single `api/router.py` builds all endpoints from the registry automatically.
- **Audit Toolset** — every create/update/delete/toggle/bulk/reorder action is logged to `AuditLog`, featuring a **Dynamic Audit Visualizer** (side-by-side diff) for changes. Entries can be pruned with the `prune_audit_log` management command.
- **Single template per operation** — `generic/list.html` and `generic/form.html` serve all content types. App-specific templates can override only what they need.
- **Centralized Media Library** — `apps/media` provides a global media picker, file-type detection, automatic background WebP thumbnail generation, and file cleanup signals on delete/replace.
- **Reusable QuerySets** — `ActiveQuerySet` and `ContentQuerySet` in `apps/core/querysets/` provide chainable `.active()`, `.published()`, `.by_position()`, `.recent()`, `.for_api()` methods.
- **Modular Permissions** — `CMSPermissionMixin` and `SuperuserRequiredMixin` for views. Custom User/Group management with granular permissions filtering.
- **SEO Toolset** — Auto-slug generation, character counters, and SEO meta panels for all content. `SlugUniqueMixin` in forms for clean form-layer validation.
- **Dashboard Caching** — Per-user stats and recent-items are cached with version-based invalidation. Any toggle, create, update, delete, or reorder bumps the version key automatically.
- **Template Tags** (`apps/core/templatetags/cms_tags`) — `get_attr` (dot-traversal), `is_media_widget`, `has_media_fields`, `split`, `getitem`.
- **Context Processor** — `cms_context` injects `cms_registry` into every template for dynamic navigation rendering.
- **Services Layer** — `apps/core/services/` houses `slug_service` (GlobalSlug query logic) and `audit_service` (log helpers), keeping views and models thin.

## Tech Stack

- **Backend**: Python 3.x, Django 5.1+, Django REST Framework (DRF), `django-cors-headers`.
- **Database**: SQLite (development) · PostgreSQL (production).
- **Image Processing**: Pillow — WebP thumbnail generation, dimension extraction.
- **Frontend**: Vanilla CSS (no frameworks), FontAwesome 6 (Icons), DataTables 2.2+ (Interactive tables), SortableJS (Drag-and-drop sorting).
- **Interactions**: Native Fetch API (AJAX), Toast notifications, Modal system.
- **Other**: `tzdata` (Windows timezone support).

## Setup

### 1. Clone & create virtualenv
```bash
git clone <repo>
cd python-cms-v2
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements/development.txt
```

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Create superuser
```bash
python manage.py createsuperuser
```

### 5. Start dev server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` — you'll be redirected to `/login/`.

## Environment Variables

| Variable                | Default (dev)         | Required in prod |
|-------------------------|-----------------------|-----------------|
| `DJANGO_ENV`            | `development`         | Set to `production` |
| `SECRET_KEY`            | insecure dev key      | ✅ Required |
| `ALLOWED_HOSTS`         | `localhost,127.0.0.1` | ✅ Required |
| `DB_NAME`               | —                     | ✅ Required (prod) |
| `DB_USER`               | —                     | ✅ Required (prod) |
| `DB_PASSWORD`           | —                     | ✅ Required (prod) |
| `DB_HOST`               | `localhost`           | Optional (prod) |
| `DB_PORT`               | `5432`                | Optional (prod) |
| `CORS_ALLOWED_ORIGINS`  | —                     | ✅ Required (prod) |

## API Endpoints

All endpoints are served under `/api/`. Anonymous access is read-only. Throttle limits apply: `120/min` (anon), `300/min` (authenticated). Results are paginated (page size: 20).

| Endpoint | Description |
|----------|-------------|
| `GET /api/articles/` | List active articles |
| `GET /api/articles/{slug}/` | Single article |
| `GET /api/blogs/` | List active blog posts |
| `GET /api/blogs/{slug}/` | Single blog post |
| `GET /api/faqs/` | List FAQ entries |
| `GET /api/packages/` | List packages with nested sub-packages |
| `GET /api/testimonials/` | List testimonials |
| `GET /api/nearbys/` | List nearby locations |
| `GET /api/socials/` | All social / OTA links |
| `GET /api/socials/?type=social` | Social links only |
| `GET /api/socials/?type=ota` | OTA/booking links only |

New content types with an `api_viewset` registered in `CMSModelConfig` are wired automatically — no changes to `api/router.py` needed.

## Production Security

The production settings (`config/settings/production.py`) automatically enable:

- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_HSTS_SECONDS = 31536000` (with subdomains + preload)

## Management Commands

| Command | Description |
|---------|-------------|
| `python manage.py prune_audit_log` | Delete audit log entries older than 90 days (configurable via `--days N`) |

## Adding a New Content Type

1.  **Create App Folder**: Create `apps/newtype/` and add an empty `__init__.py`.
2.  **Define Model**: In `apps/newtype/models.py`, extend `BaseContentModel` (for full slug + SEO support) or `SimpleContentModel` (lightweight, no slug/SEO).
3.  **Custom QuerySet** *(optional)*: Assign `objects = ContentQuerySet.as_manager()` from `apps.core.querysets.base` for chainable `.published()`, `.for_api()`, etc.
4.  **Create Forms**: In `apps/newtype/forms.py`, create a `ModelForm`. Mix in `SlugUniqueMixin` from `apps.core.forms` for form-layer slug validation (only needed for `BaseContentModel` subclasses).
5.  **Generic Views**: In `apps/newtype/views.py`, subclass `ContentListView`, `ContentCreateView`, and `ContentUpdateView` from `apps.core.generic_views`.
6.  **URLs**: Create `apps/newtype/urls.py` and include it in `config/urls.py`.
7.  **API Serializer & ViewSet**: Create `apps/newtype/api.py`.
8.  **Registration**: In `apps/newtype/apps.py`, register the model in `ready()` using `cms_registry.register`.
9.  **Settings**: Add `apps.newtype` to `INSTALLED_APPS` in `config/settings/base.py`.
10. **Database**: Run `python manage.py makemigrations && python manage.py migrate`.

The dashboard stats, recent items panel, API endpoint, toggle/bulk/sort actions, and audit log diffs all work automatically once the model is registered.

## Project Structure

```
python-cms-v2/
├── config/                     # Project configuration
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # Dev overrides (SQLite, debug toolbar)
│   │   └── production.py       # Prod overrides (PostgreSQL, HTTPS, CORS)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                   # Shared CMS infrastructure
│   │   ├── models.py           # BaseContentModel, SimpleContentModel, GlobalSlug, AuditLog
│   │   ├── mixins_models.py    # TimestampMixin, ActiveMixin, SortableMixin, SlugMixin, SEOMixin
│   │   ├── registry.py         # CMSRegistry singleton + CMSModelConfig
│   │   ├── generic_views.py    # ContentListView, ContentCreateView, ContentUpdateView
│   │   ├── mixins.py           # CMSPermissionMixin, SuperuserRequiredMixin
│   │   ├── forms.py            # SlugUniqueMixin
│   │   ├── audit.py            # log_action, log_bulk_action helpers
│   │   ├── cache.py            # invalidate_dashboard_cache (version-based)
│   │   ├── context_processors.py  # cms_context → injects cms_registry
│   │   ├── signals.py          # MediaAsset file cleanup on delete/replace
│   │   ├── views.py            # DashboardView, AuditLogView, toggle/bulk/reorder/delete endpoints
│   │   ├── urls.py
│   │   ├── querysets/
│   │   │   └── base.py         # ActiveQuerySet, ContentQuerySet
│   │   ├── services/
│   │   │   ├── audit_service.py
│   │   │   └── slug_service.py
│   │   ├── templatetags/
│   │   │   └── cms_tags.py     # get_attr, split, getitem, is_media_widget, has_media_fields
│   │   └── management/
│   │       └── commands/
│   │           └── prune_audit_log.py
│   ├── accounts/               # Custom User model, Auth, User/Group management
│   ├── media/                  # Centralized Media Library (assets, thumbnails, picker widget)
│   ├── articles/               # Article content type
│   ├── blog/                   # Blog post content type
│   ├── faq/                    # FAQ content type
│   ├── packages/               # Package + SubPackage content types
│   ├── testimonials/           # Testimonial content type
│   ├── social/                 # Social / OTA links
│   └── nearby/                 # Nearby locations content type
├── api/                        # REST API configuration (auto-wired from registry)
│   ├── router.py               # build_router() — registers all api_viewset entries
│   └── urls.py
├── templates/
│   ├── generic/                # generic/list.html + generic/form.html (serve all content types)
│   ├── core/                   # audit_log.html
│   ├── media/                  # library_grid.html, admin_list.html, widgets/
│   ├── users/                  # User & Group management templates
│   ├── accounts/               # login.html
│   ├── articles/               # Custom list override
│   ├── packages/               # subpackage_list.html
│   ├── social/                 # Custom list override
│   ├── base.html               # Main dashboard layout
│   └── dashboard.html
├── static/
│   ├── css/                    # admin.css, media-picker.css
│   ├── js/                     # admin.js (core logic), media-picker.js
│   └── img/                    # Favicon and static assets
├── media/                      # MEDIA_ROOT — uploaded files (gitignored)
├── staticfiles/                # STATIC_ROOT — collectstatic output (gitignored)
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```