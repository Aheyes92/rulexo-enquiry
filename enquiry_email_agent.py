import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
load_dotenv()

_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 587


def _smtp_credentials():
    address  = os.getenv("GMAIL_ADDRESS", "").strip()
    password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
    return address, password


def _send(from_display: str, from_address: str, to_address: str,
          subject: str, body: str) -> bool:
    _, password = _smtp_credentials()
    if not from_address or not password:
        print("[EMAIL AGENT] Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env")
        return False

    msg = MIMEMultipart()
    msg["From"]    = f"{from_display} <{from_address}>"
    msg["To"]      = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(from_address, password)
            server.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError as exc:
        print(f"[EMAIL AGENT] Auth failed: {exc}")
        return False
    except smtplib.SMTPException as exc:
        print(f"[EMAIL AGENT] SMTP error: {exc}")
        return False
    except Exception as exc:
        print(f"[EMAIL AGENT] Unexpected error: {exc}")
        return False


def send_to_prospect(lead: dict, message_content: str, client: dict) -> bool:
    gmail_address, _ = _smtp_credentials()
    prospect_email   = (lead.get("email") or "").strip()
    business_name    = client.get("business_name") or client.get("name") or "the business"
    client_name      = client.get("name") or "Your enquiry handler"

    if not prospect_email:
        print("[EMAIL AGENT] send_to_prospect: no prospect email address — skipping")
        return False

    subject = f"Re: Your enquiry to {business_name}"
    ok = _send(
        from_display=client_name,
        from_address=gmail_address,
        to_address=prospect_email,
        subject=subject,
        body=message_content,
    )
    status = "sent" if ok else "failed"
    print(f"[EMAIL AGENT] Prospect email -> {prospect_email}  [{status}]")
    return ok


def send_client_notification(lead: dict, client: dict, qualification: dict) -> bool:
    gmail_address, _ = _smtp_credentials()
    client_email     = (client.get("email") or "").strip()
    prospect_name    = lead.get("name") or "Unknown prospect"
    business_name    = client.get("business_name") or client.get("name") or "your business"

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

    body = "\n".join(body_lines)
    ok = _send(
        from_display="Rulexo System",
        from_address=gmail_address,
        to_address=client_email,
        subject=subject,
        body=body,
    )
    status = "sent" if ok else "failed"
    print(f"[EMAIL AGENT] Client notification -> {client_email}  [{status}]")
    return ok
