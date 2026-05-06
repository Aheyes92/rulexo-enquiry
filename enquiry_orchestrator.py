import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

from enquiry_receiver       import receive_lead
from enquiry_logger         import (
    log_lead, log_conversation, log_response, update_lead_status,
)
from enquiry_response_agent import generate_response
from enquiry_qualifier      import qualify_lead
from enquiry_email_agent    import send_to_prospect, send_client_notification
from enquiry_sms_agent      import send_sms_to_prospect, send_sms_to_client

_DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "enquiry.db")
DB_PATH = os.getenv("DB_PATH", _DEFAULT_DB)


def _get_client(client_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"No client found with id={client_id}")
        return dict(row)
    finally:
        conn.close()


def run_enquiry_pipeline(
    raw_data: dict,
    source: str,
    client_id: int,
    mode: str = "email_only",
) -> dict:

    print(f"\n[ORCHESTRATOR] Starting pipeline — source={source}, client_id={client_id}, mode={mode}")
    print("-" * 55)

    # ── STEP 1: normalise raw data ─────────────────────────────────────────────
    lead = receive_lead(raw_data, source)

    # ── STEP 2: log the lead ───────────────────────────────────────────────────
    lead_id = log_lead(
        client_id=client_id,
        source=lead["source"],
        name=lead.get("name"),
        phone=lead.get("phone"),
        email=lead.get("email"),
        business_type=lead.get("business_type"),
        pain_point=lead.get("pain_point"),
        message=lead.get("message"),
        budget=lead.get("budget"),
        timeframe=lead.get("timeframe"),
    )
    print(f"[ORCHESTRATOR] Lead logged — lead_id={lead_id}")

    # Log the inbound message to conversations
    log_conversation(
        lead_id=lead_id,
        client_id=client_id,
        direction="inbound",
        channel=source,
        sender=lead.get("name") or "unknown",
        message_content=lead.get("message") or lead.get("pain_point") or "",
        status="received",
    )

    # ── STEP 3: fetch client record ────────────────────────────────────────────
    client = _get_client(client_id)
    print(f"[ORCHESTRATOR] Client fetched — {client.get('name')} ({client.get('trade_type')})")

    # ── STEP 4: generate response ──────────────────────────────────────────────
    message_content = generate_response(lead, client)
    response_sent = False

    # ── STEP 5: send to prospect by email ─────────────────────────────────────
    if mode in ("email_only", "full"):
        ok = send_to_prospect(lead, message_content, client)
        if ok:
            response_sent = True

    # ── STEP 6: send to prospect by SMS ───────────────────────────────────────
    if mode in ("sms_only", "full"):
        ok = send_sms_to_prospect(lead, message_content, client)
        if ok:
            response_sent = True

    # ── STEP 7: send client notification email (always) ───────────────────────
    # Qualification hasn't run yet — pass a placeholder so notification sends immediately.
    # Client will receive accurate scores; the full record is saved in step 9.
    _placeholder_qual = {
        "intent_score": None, "urgency_score": None,
        "quality_score": None, "overall_score": "pending",
        "reason": "Qualification running — see follow-up notification.",
    }
    send_client_notification(lead, client, _placeholder_qual)

    # ── STEP 8: send client SMS if full mode ───────────────────────────────────
    if mode == "full":
        send_sms_to_client(lead, client, _placeholder_qual)

    # ── STEP 9: qualify the lead ───────────────────────────────────────────────
    qualification = qualify_lead(lead, lead_id)

    # ── STEP 10: log the outbound response ────────────────────────────────────
    channel_map = {"email_only": "email", "sms_only": "sms", "full": "email+sms"}
    channel = channel_map.get(mode, "email")
    recipient_contact = lead.get("email") if "email" in channel else lead.get("phone")

    log_response(
        lead_id=lead_id,
        client_id=client_id,
        channel=channel,
        recipient_type="lead",
        recipient_contact=recipient_contact,
        message_content=message_content,
        generated_by="claude-haiku-4-5-20251001",
        status="sent" if response_sent else "failed",
    )

    # ── STEP 11: update lead status ────────────────────────────────────────────
    update_lead_status(lead_id, "responded")
    print(f"[ORCHESTRATOR] Lead {lead_id} status -> responded")

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    summary = {
        "lead_id":        lead_id,
        "prospect_name":  lead.get("name"),
        "source":         source,
        "mode":           mode,
        "response_sent":  response_sent,
        "intent_score":   qualification["intent_score"],
        "urgency_score":  qualification["urgency_score"],
        "quality_score":  qualification["quality_score"],
        "overall_score":  qualification["overall_score"],
    }

    print("\n[ORCHESTRATOR] Pipeline complete")
    print("-" * 55)
    print(f"  lead_id        {summary['lead_id']}")
    print(f"  prospect       {summary['prospect_name']}")
    print(f"  source         {summary['source']}")
    print(f"  mode           {summary['mode']}")
    print(f"  response_sent  {summary['response_sent']}")
    print(f"  intent         {summary['intent_score']}/5")
    print(f"  urgency        {summary['urgency_score']}/5")
    print(f"  quality        {summary['quality_score']}/5")
    print(f"  overall        {summary['overall_score']}/5")
    print("-" * 55)

    return summary
