# minicom/coach.py
# AI Coach Engine — suggests messages for admins to send based on user behavior patterns.
#
# Works in two modes:
#   1. Rule-based (default, no API key needed): pattern matches common onboarding gaps.
#   2. AI-powered (optional): if OPENAI_API_KEY is set, asks an LLM for suggestions.

import os
from .models import UserEvent, Message

# ── Rule-based suggestions ────────────────────────────────────────────────────

RULE_BASED_TIPS = [
    {
        "condition": lambda events, messages: (
            any(e.event_name == "page_view" and "/dashboard" in e.metadata.get("page", "") for e in events)
            and not any(e.event_name == "checklist_step_done" for e in events)
        ),
        "suggestion": (
            "👋 Looks like {user_id} visited the dashboard but hasn't completed any setup steps yet. "
            "Consider sending: \"Need help getting started? Here's what to do first →\""
        ),
    },
    {
        "condition": lambda events, messages: (
            sum(1 for e in events if e.event_name == "idle_5min") >= 3
        ),
        "suggestion": (
            "😴 {user_id} has gone idle 3+ times. They might be stuck. "
            "Try: \"Still with us? Here's a quick 2-minute guide to get you moving →\""
        ),
    },
    {
        "condition": lambda events, messages: (
            not events  # No events at all
        ),
        "suggestion": (
            "🌱 {user_id} signed up but hasn't done anything yet. "
            "A warm welcome message within the first hour dramatically improves activation. "
            "Try: \"Welcome! Here's the one thing most users do first →\""
        ),
    },
]


def get_suggestions(app_id: str, user_id: str) -> list[dict]:
    """
    Returns a list of suggested messages an admin could send to a user.
    Each suggestion has: {"text": str, "reason": str, "confidence": str}

    Uses rule-based logic by default.
    Falls back to OpenAI if OPENAI_API_KEY is set.
    """
    events = list(UserEvent.objects.filter(app_id=app_id, user_id=user_id).order_by("-created_at")[:50])
    messages = list(Message.objects.filter(app_id=app_id, user_id=user_id).order_by("-created_at")[:20])

    suggestions = []

    if os.environ.get("OPENAI_API_KEY"):
        suggestions = _ai_suggestions(app_id, user_id, events, messages)
    else:
        suggestions = _rule_based_suggestions(user_id, events, messages)

    return suggestions


def _rule_based_suggestions(user_id: str, events, messages) -> list[dict]:
    results = []
    for rule in RULE_BASED_TIPS:
        try:
            if rule["condition"](events, messages):
                results.append({
                    "text": rule["suggestion"].format(user_id=user_id),
                    "reason": "Matched behavior pattern",
                    "confidence": "medium",
                })
        except Exception:
            pass
    return results


def _ai_suggestions(app_id: str, user_id: str, events, messages) -> list[dict]:
    """
    Uses OpenAI to generate contextual suggestions.
    Only called if OPENAI_API_KEY environment variable is set.
    """
    try:
        import openai
        openai.api_key = os.environ["OPENAI_API_KEY"]

        event_summary = ", ".join(set(e.event_name for e in events)) or "none"
        message_count = len(messages)

        prompt = (
            f"You are an onboarding coach assistant. A user (id: {user_id}) has triggered these events: {event_summary}. "
            f"They've received {message_count} messages so far. "
            f"Suggest 2 short, friendly in-app messages an admin could send to help them succeed. "
            f"Return as JSON array: [{{\"text\": \"...\", \"reason\": \"...\"}}]"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )

        import json
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)
        return [{"text": s["text"], "reason": s["reason"], "confidence": "high"} for s in parsed]

    except Exception as e:
        # Fall back to rule-based if AI fails
        return _rule_based_suggestions(user_id, [], [])
