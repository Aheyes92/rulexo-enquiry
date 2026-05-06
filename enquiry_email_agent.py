import os

import resend
from dotenv import load_dotenv
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

_FROM = "Rulexo <hello@rulexo.com>"


def _send(to_address: str, subject: str, body: str) -> bool:
    try:
        resend.Emails.send({
            "from":    _FROM,
            "to":      [to_address],
            "subject": subject,
            "text":    body,
        })
        return True
    except Exception as exc:
        print(f"[EMAIL AGENT] Resend error: {exc}")
        return False


def send_to_prospect(lead: dict, message_content: str, client: dict) -> bool:
    prospect_email = (lead.get("email") or "").strip()
    business_name  = client.get("business_name") or client.get("name") or "the business"

    if not prospect_email:
        print("[EMAIL AGENT] send_to_prospect: no prospect email address — skipping")
        return False

    subject = f"Re: Your enquiry to {business_name}"
    ok = _send(prospect_email, subject, message_content)
    print(f"[EMAIL AGENT] Prospect email -> {prospect_email}  [{'sent' if ok else 'failed'}]")
    return ok


def send_client_notification(lead: dict, client: dict, qualification: dict) -> bool:
    client_email  = (client.get("email") or "").strip()
    prospect_name = lead.get("name") or "Unknown prospect"
    business_name = client.get("business_name") or client.get("name") or "your business"

    if not client_email:
        print("[EMAIL AGENT] send_client_notification: no client email address — skipping")
        return False

    subject = f"New enquiry received - {prospect_name}"

    body_lines = [
        f"Hi {(client.get('name') or '').split()[0]},",
        "",
        f"A new enquiry has come in for {business_name}.",
        "",
        "── PROSPECT DETAILS ─────────────────────────────",
        f"Name:      {lead.get('name') or 'N/A'}",
        f"Phone:     {lead.get('phone') or 'N/A'}",
        f"Email:     {lead.get('email') or 'N/A'}",
        f"Source:    {lead.get('source') or 'N/A'}",
        "",
        "── ENQUIRY ───────────────────────────────────────",
        f"{lead.get('pain_point') or lead.get('message') or 'No details provided.'}",
        "",
    ]

    if lead.get("budget"):
        body_lines.append(f"Budget:    {lead['budget']}")
    if lead.get("timeframe"):
        body_lines.append(f"Timeframe: {lead['timeframe']}")

    body_lines += [
        "",
        "── QUALIFICATION SCORES ──────────────────────────",
        f"Intent:    {qualification.get('intent_score', 'N/A')}/5",
        f"Urgency:   {qualification.get('urgency_score', 'N/A')}/5",
        f"Quality:   {qualification.get('quality_score', 'N/A')}/5",
        f"Overall:   {qualification.get('overall_score', 'N/A')}/5",
        f"Summary:   {qualification.get('reason', 'N/A')}",
        "",
        "── STATUS ────────────────────────────────────────",
        "A personalised response has been sent to the prospect on your behalf.",
        "",
        "Rulexo Enquiry System",
    ]

    ok = _send(client_email, subject, "\n".join(body_lines))
    print(f"[EMAIL AGENT] Client notification -> {client_email}  [{'sent' if ok else 'failed'}]")
    return ok
