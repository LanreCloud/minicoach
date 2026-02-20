# AGENTS.md — Minicoach

This file provides instructions for AI coding agents (Claude Code, Codex, Cursor, etc.) working on the Minicoach project.

---

## 🧭 Project Overview

Minicoach is a Django 4.x / Python 3.10+ app. It is a fork of `colindotfun/minicom` extended with:
- Behavior-triggered messaging (`minicom/triggers.py`)
- Two-way conversation threads (`minicom/models.py` → `Conversation`, `Reply`)
- Onboarding checklist tracking (`minicom/models.py` → `ChecklistItem`, `UserProgress`)
- AI-powered tip suggestions (`minicom/coach.py`)
- User segmentation (`minicom/models.py` → `Segment`)

---

## 🛠 Dev Environment Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Tests:
```bash
python manage.py test
```

---

## 📁 Key Files & What They Do

| File | Purpose |
|------|---------|
| `minicom/models.py` | All database models. Add new fields/models here. |
| `minicom/api.py` | All `/api/` endpoints used by the widget and admin UI. |
| `minicom/triggers.py` | Engine that checks user events against trigger rules and fires messages. |
| `minicom/coach.py` | Generates suggested messages for admins using pattern matching (or LLM if API key set). |
| `minicom/static/minicoach.js` | Embeddable JS widget. Communicates with `/api/`. Keep it vanilla JS, no frameworks. |
| `testapp/views.py` | Demo application views. Shows the widget in action. |

---

## 📐 Code Conventions

- **Django ORM only** — no raw SQL unless absolutely necessary.
- **No external JS frameworks** in `minicoach.js` — vanilla JS only so it embeds in any site.
- **REST API responses** must always return JSON with keys: `status`, `data`, and optionally `error`.
- **Models** should have `created_at = models.DateTimeField(auto_now_add=True)` on every new model.
- **Triggers** are evaluated lazily on each user event POST to `/api/event/` — keep the trigger engine fast.

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Set to `False` in production | No (defaults True) |
| `OPENAI_API_KEY` | Enables AI tip suggestions in `coach.py` | No |
| `DATABASE_URL` | Postgres URL (defaults to SQLite) | No |

---

## ✅ Definition of Done

A feature is complete when:
1. Model migrations are generated and applied (`python manage.py makemigrations && migrate`)
2. API endpoint returns correct JSON shape
3. Widget (`minicoach.js`) reflects the change if user-facing
4. At least one Django test exists in `minicom/tests.py`
5. `README.md` is updated if new setup steps are required

---

## 🚫 Do Not

- Do not modify `testapp/fixtures/` without regenerating with `python manage.py dumpdata`
- Do not add jQuery or React to `minicoach.js`
- Do not expose the admin API endpoints without checking `request.user.is_staff`
- Do not store secrets in code — use environment variables

---

## 💡 Good First Tasks for Agents

1. Add a `read_at` timestamp to the `Message` model and expose it in the widget
2. Add a `/api/segment/` endpoint that returns which segments a given `user_id` belongs to
3. Write tests for the trigger engine in `minicom/triggers.py`
4. Add a `priority` field to `Message` (low/normal/high) and sort the widget inbox accordingly
