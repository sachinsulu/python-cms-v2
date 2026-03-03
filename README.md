# Python CMS v2

A production-grade Django CMS rebuilt from scratch with proper architecture.

## Architecture Highlights

- **`BaseContentModel`** — single abstract base for all content types (slug, is_active, position, timestamps, SEO meta)
- **Registry pattern** — apps self-register via `AppConfig.ready()`. Adding a new content type requires zero changes to shared code.
- **Generic CRUD views** — `ContentListView`, `ContentCreateView`, `ContentUpdateView`. Each app subclasses these with a few class attributes.
- **Auto-wired REST API** — a single `api/router.py` builds all endpoints from the registry automatically.
- **Audit logging** — every create/update/delete/toggle/bulk action is logged to `AuditLog`.
- **Single template per operation** — `generic/list.html` and `generic/form.html` serve all content types.
- **Centralized Media Library** — `apps/media` provides a global media picker and automatic WebP thumbnail generation.

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

All endpoints are read-only and versioned under `/api/v1/`.

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/articles/` | List active articles |
| `GET /api/v1/articles/{slug}/` | Single article |
| `GET /api/v1/blogs/` | List active blog posts |
| `GET /api/v1/packages/` | List packages with nested sub-packages |
| `GET /api/v1/testimonials/` | List testimonials |
| `GET /api/v1/nearbys/` | List nearby locations |
| `GET /api/v1/socials/?type=social` | Social links |
| `GET /api/v1/socials/?type=ota` | OTA/booking links |

## Adding a New Content Type

1. Create `apps/newtype/models.py` — extend `BaseContentModel`
2. Create `apps/newtype/forms.py` — standard Django ModelForm
3. Create `apps/newtype/views.py` — subclass the 3 generic views
4. Create `apps/newtype/urls.py`
5. Create `apps/newtype/api.py` — serializer + ViewSet
6. Create `apps/newtype/apps.py` — register in `ready()`
7. Add to `INSTALLED_APPS` in `config/settings/base.py`
8. Include URLs in `config/urls.py`
9. Run `python manage.py makemigrations && python manage.py migrate`

The dashboard stat, API endpoint, toggle/bulk/sort, and audit log all work automatically.

## Project Structure

```
python-cms-v2/
├── config/           # Project config (settings, urls, wsgi)
│   └── settings/     # base / development / production
├── apps/
│   ├── core/         # Registry, BaseContentModel, AuditLog, generic views
│   ├── accounts/     # Custom User model, auth, user/group management
│   ├── media/        # Centralized Media Library (assets, thumbnails)
│   ├── articles/     # Article content type
│   ├── blog/         # Blog post content type
│   ├── packages/     # Package + SubPackage content types
│   ├── testimonials/ # Testimonial content type
│   ├── social/       # Social / OTA links
│   └── nearby/       # Nearby locations content type
├── api/              # REST API router (auto-wired from registry)
├── templates/
│   ├── generic/      # list.html + form.html (shared by all content types)
│   ├── base.html
│   ├── dashboard.html
│   └── [per-app overrides]
├── static/
│   ├── css/admin.css
│   └── js/admin.js
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```
