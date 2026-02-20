# minicom/triggers.py
# Behavior Trigger Engine — the core of what makes Minicoach different from Minicom.
#
# How it works:
#   1. The embedded widget posts a UserEvent to /api/event/ whenever something happens
#      (e.g. user visits a page, completes a step, goes idle).
#   2. evaluate_triggers() runs against all active TriggerRules for that app.
#   3. If a rule matches, a Message is created and queued for that user.

from .models import TriggerRule, Message, UserEvent, Conversation
import logging

logger = logging.getLogger(__name__)


def evaluate_triggers(app_id: str, user_id: str, event_name: str, metadata: dict):
    """
    Called every time a user event arrives.
    Checks all active TriggerRules for the given app and fires any that match.

    Args:
        app_id:     The app's API key / identifier.
        user_id:    The end-user's identifier (from the embedding site).
        event_name: A string like "page_view", "idle_5min", "checklist_step_done".
        metadata:   Extra context, e.g. {"page": "/dashboard", "step": "connect_integration"}.

    Returns:
        List of Message objects that were created (may be empty).
    """
    fired = []

    # Fetch all active rules for this app that match this event
    rules = TriggerRule.objects.filter(
        app_id=app_id,
        trigger_event=event_name,
        is_active=True,
    )

    for rule in rules:
        # Check if this user already received this message (avoid spam)
        already_sent = Message.objects.filter(
            app_id=app_id,
            user_id=user_id,
            trigger_rule=rule,
        ).exists()

        if already_sent and not rule.allow_repeat:
            continue

        # Check metadata conditions if the rule has any
        if rule.condition_key and rule.condition_value:
            actual_value = str(metadata.get(rule.condition_key, ""))
            if actual_value != rule.condition_value:
                continue

        # All checks passed — fire the message
        try:
            conversation = Conversation.objects.get_or_create(
                app_id=app_id,
                user_id=user_id,
            )[0]

            msg = Message.objects.create(
                app_id=app_id,
                user_id=user_id,
                conversation=conversation,
                trigger_rule=rule,
                body=rule.message_body,
                sender_name=rule.sender_name or "Coach",
            )
            fired.append(msg)
            logger.info(f"Trigger fired: rule={rule.id} user={user_id} event={event_name}")

        except Exception as e:
            logger.error(f"Failed to fire trigger rule {rule.id}: {e}")

    return fired


def get_pending_messages(app_id: str, user_id: str) -> list:
    """
    Returns all unread messages for a user, ordered oldest first.
    The widget polls this to display the coach bubble.
    """
    return list(
        Message.objects.filter(
            app_id=app_id,
            user_id=user_id,
            is_read=False,
        ).order_by("created_at").values("id", "body", "sender_name", "created_at")
    )
