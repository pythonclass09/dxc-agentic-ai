from __future__ import annotations

import re


_PRIORITY_SLA = {
    "P1": 2,
    "P2": 8,
    "P3": 24,
    "P4": 72,
}

_QUEUE_RULES = (
    ("Security", ("phishing", "breach", "malware")),
    ("Network", ("vpn", "wifi", "network")),
    ("Access", ("password", "login", "locked")),
    ("Hardware", ("laptop", "keyboard", "screen")),
)

def _word_pattern(word: str) -> re.Pattern[str]:
    return re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)


def triage(ticket: dict) -> dict:
    title = ticket.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title is required")

    description = ticket.get("description")
    if description is None:
        description = ""
    if not isinstance(description, str):
        description = str(description)

    affected_users = ticket.get("affected_users", 1)
    if not isinstance(affected_users, int) or affected_users < 1:
        raise ValueError("affected_users must be a positive int")

    customer_tier = ticket.get("customer_tier", "standard")
    if customer_tier not in {"standard", "vip"}:
        raise ValueError("customer_tier must be 'standard' or 'vip'")

    text = f"{title} {description}"

    if affected_users >= 50 or _word_pattern("outage").search(text) or _word_pattern("down").search(text):
        priority = "P1"
    elif affected_users >= 10 or _word_pattern("urgent").search(text) or _word_pattern("blocked").search(text):
        priority = "P2"
    elif affected_users >= 2:
        priority = "P3"
    else:
        priority = "P4"

    if customer_tier == "vip":
        priority = {"P4": "P3", "P3": "P2", "P2": "P1", "P1": "P1"}[priority]

    queue = "General"
    for queue_name, words in _QUEUE_RULES:
        if any(_word_pattern(word).search(text) for word in words):
            queue = queue_name
            break

    return {"priority": priority, "queue": queue, "sla_hours": _PRIORITY_SLA[priority]}
