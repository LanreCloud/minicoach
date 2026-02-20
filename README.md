# 🧠 Minicoach — Smart Onboarding, Built on Minicom

> A fork of [colindotfun/minicom](https://github.com/colindotfun/minicom) — extended into an intelligent user onboarding coach for SaaS apps.

**Trac Address:** `YOUR_TRAC_WALLET_ADDRESS_HERE`

---

## What is Minicoach?

Minicom lets site admins send one-way messages to users. **Minicoach goes further** — it watches user behavior and automatically sends personalized, contextual tips at exactly the right moment.

Think of it as the difference between a newsletter and a personal trainer.

| Minicom | Minicoach |
|--------|-----------|
| Admin sends message | App sends message automatically |
| Same message for all users | Personalized per user |
| Manual triggers | Behavior-triggered |
| One-way | Two-way conversation |

---

## ✨ New Features (vs original Minicom)

- **Behavior triggers** — Messages fire based on what users do (or don't do)
- **Two-way replies** — Users can respond; admins see a conversation thread
- **Onboarding checklists** — Track user progress through setup steps
- **Auto-coach mode** — AI-generated tip suggestions for admins
- **User segments** — Target messages to specific groups (new users, power users, etc.)

---

## 🚀 Getting Started

You need Python 3.10+ and pip.

```bash
git clone https://github.com/YOUR_USERNAME/minicoach
cd minicoach
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin` for the admin dashboard.
Visit `http://127.0.0.1:8000/demo` to see the embedded widget in action.

---

## 🗂 Project Structure

```
minicoach/
├── minicom/
│   ├── models.py        # Message, Conversation, UserEvent, Segment models
│   ├── api.py           # REST API for widget + admin
│   ├── triggers.py      # Behavior trigger engine (NEW)
│   ├── coach.py         # AI tip suggestion engine (NEW)
│   └── static/
│       └── minicoach.js # Embeddable widget (extended from minicom.js)
├── testapp/             # Demo app showing Minicoach in action
├── AGENTS.md            # Instructions for AI coding agents
└── manage.py
```

---

## 🤝 Contributing

PRs welcome! Check `AGENTS.md` for how to work with this codebase using AI coding tools.

---

## 📜 License

MIT — same as the original Minicom project.
