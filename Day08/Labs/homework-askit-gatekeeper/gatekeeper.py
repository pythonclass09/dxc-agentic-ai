"""AskIT Gatekeeper safety checks."""

import re

D1_APPROVAL = "no"
D2_APPROVER = "on-call"
REMEMBER_FOR_DAYS = 30

VIP_USERS = {"EMP-1001", "EMP-1012", "EMP-1023"}
READ_ACTIONS = {"search_kb", "get_ticket"}
WRITE_ACTIONS = {"reset_password", "update_ticket", "grant_access"}
ALL_ACTIONS = READ_ACTIONS | WRITE_ACTIONS

ROUTE_RULES = (
    ("Security", ("phishing", "malware", "breach", "suspicious", "ransomware")),
    ("Access", ("password", "locked", "login", "mfa", "access")),
    ("Network", ("vpn", "wifi", "network", "internet")),
    ("Hardware", ("laptop", "printer", "screen", "keyboard", "phone")),
)

SECRET_WORDS = ("password", "passcode", "otp", "pin")


def _whole_word_match(text: str, word: str) -> bool:
    pattern = r"(?i)(?<!\w)" + re.escape(word) + r"(?!\w)"
    return re.search(pattern, text) is not None


def route(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")

    for team, keywords in ROUTE_RULES:
        if any(_whole_word_match(text, keyword) for keyword in keywords):
            return team

    return "General"


def needs_approval(action: str, user_id: str, hour: int) -> dict:
    if action not in ALL_ACTIONS:
        raise ValueError("invalid action")
    if not isinstance(hour, int) or isinstance(hour, bool) or not 0 <= hour <= 23:
        raise ValueError("hour must be an int from 0 to 23")

    is_vip = user_id in VIP_USERS
    is_night = hour >= 20 or hour < 8

    if action in READ_ACTIONS:
        if is_vip:
            return {"approval": D1_APPROVAL == "yes", "approver": "it manager" if D1_APPROVAL == "yes" else "none"}
        return {"approval": False, "approver": "none"}

    if is_vip:
        return {"approval": True, "approver": "it manager"}
    if is_night:
        return {"approval": True, "approver": D2_APPROVER}
    return {"approval": True, "approver": "service desk lead"}


def safe_to_remember(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False

    normalized = text.lower()

    if any(_whole_word_match(normalized, word) for word in SECRET_WORDS):
        return False

    if re.search(r"(?i)\bhome\s+address\b|\baddress\b", text):
        return False

    compact_text = re.sub(r"[\s\-]+", "", text)
    if re.search(r"\d{6,}", compact_text):
        return False

    return True
