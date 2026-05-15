# JORDROP Esports

JORDROP Esports is a Django-based esports knowledge platform that combines game profiles, team and player directories, tournament tracking, moderated wiki publishing, and an AI assistant powered by Groq. The project is designed as a community-editable hub where visitors can browse competitive esports information while contributors and moderators manage reliable wiki content through a controlled review workflow.

## Overview

The site is organized around esports games. Each game can have teams, players, wiki pages, and tournaments attached to it. Public users can browse published content, registered contributors can submit new wiki pages or edit requests, and moderators can approve, reject, or restore wiki revisions.

The platform also includes a floating JORDROP AI chat widget that sends user prompts to a server-side Groq integration using `llama-3.1-8b-instant`. The API key stays on the Django server and is never exposed to the browser.

## Core Features

- Game, team, and player profile pages with local media support and external image URLs.
- Wiki pages with immutable revision history, Markdown rendering, sanitized HTML output, and restore support.
- Contributor edit requests with moderator approval and rejection workflows.
- Tournament and match tracking with bracket-oriented match progression.
- Global search across wiki pages, teams, and players.
- Django REST Framework API endpoints for games, teams, players, wiki pages, revisions, edit requests, and tournaments.
- JWT authentication endpoints for API clients.
- Groq-powered AI chat endpoint at `/api/ai/chat/`.
- Role-based access control for visitors, contributors, moderators, and admins.

## Tech Stack

- Python and Django
- Django REST Framework
- Simple JWT
- SQLite for local development
- HTML, CSS, and JavaScript
- Markdown and Bleach for wiki rendering and sanitization
- Pillow for uploaded images
- Groq chat completions API

## Environment Variables

Create a `.env` file in the Django project directory. At minimum, set:

```env
GROQ_API_KEY=your_groq_api_key
```

Optional values:

```env
GROQ_MODEL=llama-3.1-8b-instant
GROQ_REQUEST_TIMEOUT=20
PANDASCORE_API_TOKEN=your_pandascore_token
```

The `.env` file is ignored by Git and should not be committed.

## Running Locally

From the `jordrop` directory:

```bash
python manage.py migrate
python manage.py runserver
```

Visit:

```text
http://127.0.0.1:8000/
```

Admin is available at:

```text
http://127.0.0.1:8000/admin/
```

## Tests

Run the focused API tests:

```bash
python manage.py test apps.api.tests
```

Run Django system checks:

```bash
python manage.py check
```

## Project Structure

```text
apps/
  api/          REST API, JWT routes, and Groq AI chat endpoint
  core/         Shared abstract models
  games/        Game, team, and player models and views
  tournaments/ Tournament and match models
  users/        Custom user model, roles, forms, and auth views
  wiki/         Wiki pages, revisions, edit requests, moderation, and search
templates/     Shared and app-specific Django templates
static/        Static assets
jordrop/       Django project settings and root URL configuration
```

## Security Notes

- Groq requests are proxied through Django so the browser never receives `GROQ_API_KEY`.
- Wiki Markdown is rendered to sanitized HTML with Bleach.
- Forms use Django CSRF protection.
- The AI chat endpoint includes basic anonymous throttling to avoid unlimited public proxy usage.
