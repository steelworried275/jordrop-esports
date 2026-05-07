# JORDROP Esports — Redesigned

A Wikipedia-like esports platform with wiki revision history, collaborative editing,
role-based access control, a REST API, and tournament bracket generation.

---

## Quick start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Create a superuser (give yourself the admin role via Django admin after login)
python manage.py createsuperuser

# 5. Run the dev server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** — admin panel at **/admin/**.

---

## App structure

```
apps/
├── core/          Abstract base models (TimeStampedModel, SluggedModel)
├── users/         Custom User with role field + decorators + RBAC enforcement
├── games/         Game, Team, Player
├── wiki/          Page, PageRevision, EditRequest — the full wiki engine
├── tournaments/   Tournament, Match + bracket generation service
└── api/           Django REST Framework endpoints + JWT auth
```

---

## Key features implemented

### Wiki system
- **`Page`** — stores metadata only; content lives in revisions
- **`PageRevision`** — immutable snapshots, auto-numbered, Markdown → bleach-sanitised HTML
- **`EditRequest`** — contributor submits → `status=pending` → moderator approves/rejects
- **Restore** any past revision via moderator action
- **Diff view** between consecutive revisions using Python `difflib`

### RBAC (Role-Based Access Control)
| Role | Can do |
|------|--------|
| Visitor | Read all public content |
| Contributor | Submit wiki edits, create pages |
| Moderator | Approve/reject edits, restore revisions |
| Admin | Everything above + Django admin |

Roles are enforced via `@contributor_required` / `@moderator_required` decorators in every view.
New registrations default to **Contributor**.

### REST API (`/api/`)
- Browsable API at `/api/`
- JWT auth: `POST /api/auth/token/` → bearer token
- Endpoints: `games`, `teams`, `players`, `pages`, `revisions`, `edit-requests`, `tournaments`
- Custom actions: `POST /api/edit-requests/{id}/approve/` and `/reject/`

### Tournament brackets
- `format` field: single elimination, double elimination, round robin
- `Match.next_match` self-FK wires bracket structure
- Admin action **"Generate single-elimination bracket"** auto-creates all matches
- Winners automatically slot into the next match on save

### Search
- Global search at `/search/?q=` covering wiki pages, teams, players
- Search bar in the nav on every page

### Security
- CSRF tokens on all forms
- `bleach` sanitises all Markdown-rendered HTML before storage
- No admin links in public templates
- Security headers configured in `settings.py`
- `python manage.py check --deploy` passes cleanly

---

## Running tests

```bash
python manage.py test apps.wiki apps.tournaments apps.users apps.api
```

---

## Switching to PostgreSQL

Uncomment the PostgreSQL `DATABASES` block in `settings.py`, install `psycopg2-binary`,
and run `python manage.py migrate`. PostgreSQL enables full-text search via
`django.contrib.postgres.search.SearchVector`.

---

## API usage examples

```bash
# Get a JWT token
curl -X POST http://localhost:8000/api/auth/token/ \
  -d '{"username":"mod","password":"pass"}' \
  -H "Content-Type: application/json"

# List wiki pages
curl http://localhost:8000/api/pages/

# Approve an edit (moderator token required)
curl -X POST http://localhost:8000/api/edit-requests/1/approve/ \
  -H "Authorization: Bearer <token>"
```
