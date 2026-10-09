def triage(ticket):
    title = str(ticket.get("title", "")).lower()
    description = str(ticket.get("description", "")).lower()
    affected_users = ticket.get("affected_users", 0)

    text = f"{title} {description}"

    if any(word in text for word in ["outage", "down", "critical", "urgent", "sev1", "severe"]):
        priority = "P1"
        queue = "incident"
        sla_hours = 1
    elif any(word in text for word in ["broken", "error", "failed", "cannot", "unable", "blocked"]):
        priority = "P2"
        queue = "support"
        sla_hours = 4
    elif affected_users >= 50:
        priority = "P2"
        queue = "support"
        sla_hours = 4
    elif affected_users >= 10:
        priority = "P3"
        queue = "support"
        sla_hours = 8
    else:
        priority = "P4"
        queue = "service"
        sla_hours = 24

    return {"priority": priority, "queue": queue, "sla_hours": sla_hours}
