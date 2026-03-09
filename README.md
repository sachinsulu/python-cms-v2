# Python CMS v2

A production-grade Django CMS rebuilt from scratch with proper architecture.

## Architecture Highlights

- **`BaseContentModel`** — single abstract base for all content types (slug, is_active, position, timestamps, SEO meta).
- **Registry pattern** — apps self-register via `AppConfig.ready()`. Adding a new content type requires zero changes to shared code.
- **Generic CRUD views** — `ContentListView`, `ContentCreateView`, `ContentUpdateView`. Each app subclasses these with a few class attributes.
- **Auto-wired REST API** — a single `api/router.py` builds all endpoints from the registry automatically.
- **Audit Toolset** — every create/update/delete/toggle/bulk action is logged to `AuditLog`, featuring a **Dynamic Audit Visualizer** (side-by-side diff) for changes.
- **Single template per operation** — `generic/list.html` and `generic/form.html` serve all content types.
- **Centralized Media Library** — `apps/media` provides a global media picker and automatic WebP thumbnail generation.
- **Modular Permissions** — Custom User/Group management with granular permissions filtering.
- **SEO Toolset** — Auto-slug generation, character counters, and SEO meta panels for all content.

## Tech Stack

- **Backend**: Python 3.x, Django 5.1+, Django REST Framework (DRF).
- **Frontend**: Vanilla CSS (no frameworks), FontAwesome 6 (Icons), DataTables 2.2+ (Interactive tables), SortableJS (Drag-and-drop sorting).
- **Interactions**: Native Fetch API (AJAX), Toast notifications, Modal system.

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

| Variable       | Default (dev)        | Required in prod |
|----------------|----------------------|-----------------|
| `DJANGO_ENV`   | `development`        | Set to `production` |
| `SECRET_KEY`   | insecure dev key     | ✅ Required |
| `ALLOWED_HOSTS`| `localhost,127.0.0.1`| ✅ Required |
| `DB_NAME`      | —                    | ✅ Required (prod) |
| `DB_USER`      | —                    | ✅ Required (prod) |
| `DB_PASSWORD`  | —                    | ✅ Required (prod) |

## API Endpoints

All endpoints are read-only and versioned under `/api/`.

| Endpoint | Description |
|----------|-------------|
| `GET /api/articles/` | List active articles |
| `GET /api/articles/{slug}/` | Single article |
| `GET /api/blogs/` | List active blog posts |
| `GET /api/faqs/` | List FAQ entries |
| `GET /api/packages/` | List packages with nested sub-packages |
| `GET /api/testimonials/` | List testimonials |
| `GET /api/nearbys/` | List nearby locations |
| `GET /api/socials/?type=social` | Social links |
| `GET /api/socials/?type=ota` | OTA/booking links |

## Adding a New Content Type

1.  **Create App Folder**: Create `apps/newtype/` and add an empty `__init__.py`.
2.  **Define Model**: In `apps/newtype/models.py`, extend `BaseContentModel` (or `SimpleContentModel`).
3.  **Create Forms**: In `apps/newtype/forms.py`, create a standard `ModelForm`.
4.  **Generic Views**: In `apps/newtype/views.py`, subclass `ContentListView`, `ContentCreateView`, and `ContentUpdateView` from `apps.core.generic_views`.
5.  **URLs**: Create `apps/newtype/urls.py` and include it in `config/urls.py`.
6.  **API Serializer & ViewSet**: Create `apps/newtype/api.py`.
7.  **Registration**: In `apps/newtype/apps.py`, register the model in `ready()` using `cms_registry.register`.
8.  **Settings**: Add `apps.newtype` to `INSTALLED_APPS` in `config/settings/base.py`.
9.  **Database**: Run `python manage.py makemigrations && python manage.py migrate`.

The dashboard stats, API endpoint, toggle/bulk/sort, and audit log diffs all work automatically once registered.

## Project Structure

```
python-cms-v2/
├── config/           # Project configuration (settings, urls, wsgi)
│   └── settings/     # base / development / production settings
├── apps/
│   ├── core/         # Registry, BaseContentModel, AuditLog, generic views, mixins
│   ├── accounts/     # Custom User model, Auth, User/Group management
│   ├── media/        # Centralized Media Library (assets, thumbnails, picker)
│   ├── articles/     # Article content type
│   ├── blog/         # Blog post content type
│   ├── faq/          # FAQ content type
│   ├── packages/     # Package + SubPackage content types
│   ├── testimonials/ # Testimonial content type
│   ├── social/       # Social / OTA links
│   └── nearby/       # Nearby locations content type
├── api/              # REST API configuration (auto-wired from registry)
├── templates/
│   ├── generic/      # Shared list.html + form.html for all content types
│   ├── users/        # User/Group management templates
│   ├── base.html     # Main dashboard layout
│   └── dashboard.html
├── static/
│   ├── css/          # admin.css, media-picker.css
│   ├── js/           # admin.js (core logic), media-picker.js
│   └── img/          # Favicon and static assets
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

