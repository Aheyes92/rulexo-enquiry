from enquiry_logger import log_qualification

# ── KEYWORD LISTS ──────────────────────────────────────────────────────────────

_URGENCY_HIGH = {
    "urgent", "asap", "emergency", "immediately", "today",
    "right now", "straight away", "right away", "as soon as possible",
}
_URGENCY_MED = {
    "this week", "within days", "few days", "this weekend", "by friday",
    "end of week",
}
_URGENCY_LOW = {
    "next week", "within 2 weeks", "within a fortnight", "soon",
    "coming week",
}
_URGENCY_MODERATE = {
    "next month", "within a month", "in a few weeks", "a few weeks",
    "few weeks", "coming month",
}


# ── SCORING HELPERS ────────────────────────────────────────────────────────────

def _intent_score(lead: dict) -> int:
    score = 1
    msg = (lead.get("message") or "").strip()
    pain = (lead.get("pain_point") or "").strip()
    budget = (lead.get("budget") or "").strip()
    timeframe = (lead.get("timeframe") or "").strip()

    if len(msg) > 20 or len(pain) > 20:
        score += 1
    if budget:
        score += 1
    if timeframe:
        score += 1
    if len(msg) > 100 or len(pain) > 100:
        score += 1

    return min(score, 5)


def _urgency_score(lead: dict) -> int:
    text = " ".join(filter(None, [
        lead.get("message"), lead.get("pain_point"), lead.get("timeframe"),
    ])).lower()

    if any(kw in text for kw in _URGENCY_HIGH):
        return 5
    if any(kw in text for kw in _URGENCY_MED):
        return 4
    if any(kw in text for kw in _URGENCY_LOW):
        return 3
    if any(kw in text for kw in _URGENCY_MODERATE):
        return 2
    return 1


def _quality_score(lead: dict) -> int:
    score = 1
    if lead.get("name"):
        score += 1
    if lead.get("phone"):
        score += 1
    if lead.get("email"):
        score += 1
    msg = (lead.get("message") or lead.get("pain_point") or "")
    if len(msg) > 30:
        score += 1
    return min(score, 5)


def _build_reason(intent: int, urgency: int, quality: int) -> str:
    parts = []

    if intent >= 4:
        parts.append("High intent prospect with specific job details")
    elif intent == 3:
        parts.append("Moderate intent with some job details provided")
    else:
        parts.append("Low intent — limited job information provided")

    if urgency >= 4:
        parts.append("strong urgency signals present")
    elif urgency == 3:
        parts.append("near-term timeframe mentioned")
    elif urgency == 2:
        parts.append("loose timeframe indicated")
    else:
        parts.append("no urgency signals detected")

    if quality >= 4:
        parts.append("complete contact information")
    elif quality == 3:
        parts.append("partial contact information")
    else:
        parts.append("limited contact information")

    base = ". ".join([parts[0].capitalize(), parts[1].capitalize(), parts[2].capitalize()])

    if intent >= 4 and urgency >= 4:
        base += ". Priority follow-up recommended."
    elif intent >= 3 or quality >= 4:
        base += ". Standard follow-up recommended."
    else:
        base += ". Follow up when capacity allows."

    return base


# ── MAIN FUNCTION ──────────────────────────────────────────────────────────────

def qualify_lead(lead: dict, lead_id: int) -> dict:
    intent = _intent_score(lead)
    urgency = _urgency_score(lead)
    quality = _quality_score(lead)
    overall = round((intent + urgency + quality) / 3, 1)
    reason = _build_reason(intent, urgency, quality)

    result = {
        "intent_score":   intent,
        "urgency_score":  urgency,
        "quality_score":  quality,
        "overall_score":  overall,
        "decision":       "respond",
        "reason":         reason,
    }

    log_qualification(
        lead_id=lead_id,
        score=int(overall * 20),  # store as 0-100 integer (5.0 -> 100)
        decision="respond",
        reason=reason,
    )

    print(f"[QUALIFIER] lead_id={lead_id}")
    print(f"  intent_score   {intent}/5")
    print(f"  urgency_score  {urgency}/5")
    print(f"  quality_score  {quality}/5")
    print(f"  overall_score  {overall}/5")
    print(f"  decision       {result['decision']}")
    print(f"  reason         {reason}")
    print()

    return result
