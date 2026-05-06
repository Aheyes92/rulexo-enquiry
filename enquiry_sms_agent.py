import os

from dotenv import load_dotenv
load_dotenv()


def _twilio_credentials():
    sid   = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    phone = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
    return sid, token, phone


def _credentials_present() -> bool:
    sid, token, phone = _twilio_credentials()
    return bool(sid and token and phone)


def send_sms_to_prospect(lead: dict, message_content: str, client: dict) -> bool:
    if not _credentials_present():
        print("[SMS AGENT] SMS stubbed — Twilio not configured")
        return False

    prospect_phone = (lead.get("phone") or "").strip()
    if not prospect_phone:
        print("[SMS AGENT] send_sms_to_prospect: no prospect phone number — skipping")
        return False

    sid, token, from_phone = _twilio_credentials()

    # Truncate to 1600 chars (Twilio limit for concatenated SMS)
    sms_body = message_content[:1600]

    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        twilio_client = Client(sid, token)
        message = twilio_client.messages.create(
            body=sms_body,
            from_=from_phone,
            to=prospect_phone,
        )
        print(f"[SMS AGENT] Prospect SMS -> {prospect_phone}  [sent, sid={message.sid}]")
        return True

    except TwilioRestException as exc:
        print(f"[SMS AGENT] Twilio error: {exc}")
        return False
    except Exception as exc:
        print(f"[SMS AGENT] Unexpected error: {exc}")
        return False


def send_sms_to_client(lead: dict, client: dict, qualification: dict) -> bool:
    if not _credentials_present():
        print("[SMS AGENT] SMS stubbed — Twilio not configured")
        return False

    client_phone = (client.get("phone") or "").strip()
    if not client_phone:
        print("[SMS AGENT] send_sms_to_client: no client phone number — skipping")
        return False

    prospect_name = lead.get("name") or "Unknown"
    source        = lead.get("source") or "unknown"
    overall       = qualification.get("overall_score", "N/A")

    sms_body = (
        f"New enquiry from {prospect_name} via {source}. "
        f"Response sent automatically. "
        f"Overall score: {overall}/5. "
        f"Check email for full details."
    )

    sid, token, from_phone = _twilio_credentials()

    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        twilio_client = Client(sid, token)
        message = twilio_client.messages.create(
            body=sms_body,
            from_=from_phone,
            to=client_phone,
        )
        print(f"[SMS AGENT] Client SMS -> {client_phone}  [sent, sid={message.sid}]")
        return True

    except TwilioRestException as exc:
        print(f"[SMS AGENT] Twilio error: {exc}")
        return False
    except Exception as exc:
        print(f"[SMS AGENT] Unexpected error: {exc}")
        return False
