# ── FIELD MAPS ─────────────────────────────────────────────────────────────────
# Maps standard schema fields -> source-specific field names for each platform.
# If a platform doesn't carry a field the key maps to None so .get() returns None.

_SOURCE_MAPS = {
    "website": {
        "name":          "name",
        "phone":         "phone",
        "email":         "email",
        "business_type": "business_type",
        "pain_point":    "pain_point",
        "message":       "message",
        "budget":        "budget",
        "timeframe":     "timeframe",
    },
    "bark": {
        "name":          "contact_name",
        "phone":         "contact_phone",
        "email":         "contact_email",
        "business_type": "category",
        "pain_point":    "description",
        "message":       "description",
        "budget":        "budget",
        "timeframe":     "timeframe",
    },
    "facebook": {
        "name":          "full_name",
        "phone":         "phone_number",
        "email":         "email",
        "business_type": "job_type",
        "pain_point":    "additional_info",
        "message":       "additional_info",
        "budget":        "budget",
        "timeframe":     "timeframe",
    },
    "checkatrade": {
        "name":          "customer_name",
        "phone":         "telephone",
        "email":         "email_address",
        "business_type": "trade_required",
        "pain_point":    "job_description",
        "message":       "job_description",
        "budget":        "budget",
        "timeframe":     "timeframe",
    },
}

_STANDARD_FIELDS = [
    "name", "phone", "email", "business_type",
    "pain_point", "message", "budget", "timeframe",
]


# ── MAIN FUNCTION ──────────────────────────────────────────────────────────────

def receive_lead(raw_data: dict, source: str) -> dict:
    source = source.lower().strip()

    field_map = _SOURCE_MAPS.get(source)
    if field_map is None:
        print(f"[RECEIVER] Warning: unknown source '{source}'. Attempting direct field match.")
        field_map = {f: f for f in _STANDARD_FIELDS}

    normalised = {}
    for standard_field in _STANDARD_FIELDS:
        source_key = field_map.get(standard_field)
        value = raw_data.get(source_key) if source_key else None
        normalised[standard_field] = value or None

    normalised["source"] = source

    print(f"[RECEIVER] Normalised lead from '{source}':")
    for k, v in normalised.items():
        display = f'"{v}"' if v else "None"
        print(f"  {k:<16} {display}")
    print()

    return normalised
