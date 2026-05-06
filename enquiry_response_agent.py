import os

import anthropic
from dotenv import load_dotenv
load_dotenv()

_DEFAULT_VOICE = (
    "Friendly, warm and professional. Respond as if you are the business owner personally "
    "replying. Use the prospect's first name. Keep it brief and human. Always state a clear "
    "next step. Sign off with the client's first name."
)

_CLIENT = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_response(lead: dict, client: dict) -> str:
    prospect_first = (lead.get("name") or "there").split()[0]
    client_first   = (client.get("name") or "").split()[0]
    business_name  = client.get("business_name") or client.get("name") or "the business"
    trade_type     = client.get("trade_type") or "trade professional"
    voice_profile  = (client.get("voice_profile") or "").strip() or _DEFAULT_VOICE

    enquiry_text = " ".join(filter(None, [
        lead.get("pain_point"), lead.get("message"),
    ])).strip() or "General enquiry — no details provided."

    source = lead.get("source", "unknown")
    budget = lead.get("budget")
    timeframe = lead.get("timeframe")

    context_lines = [f"Source platform: {source}"]
    if budget:
        context_lines.append(f"Budget mentioned: {budget}")
    if timeframe:
        context_lines.append(f"Timeframe mentioned: {timeframe}")

    system_prompt = (
        f"You are {client_first}, the owner of {business_name}, a {trade_type} business. "
        f"Tone and style: {voice_profile}"
    )

    user_prompt = (
        f"A new enquiry has come in. Write a personalised reply to send directly to the prospect.\n\n"
        f"Prospect name: {lead.get('name') or 'Unknown'}\n"
        f"Their enquiry: {enquiry_text}\n"
        f"{chr(10).join(context_lines)}\n\n"
        f"Write the response now. Do not add a subject line. Do not include any preamble or "
        f"explanation — just the email body, starting with the greeting."
    )

    try:
        message = _CLIENT.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        response_text = message.content[0].text.strip()
        print(f"[RESPONSE AGENT] Generated response for {prospect_first} "
              f"({len(response_text)} chars, model={message.model})")
        return response_text

    except anthropic.APIError as exc:
        print(f"[RESPONSE AGENT] API error: {exc}")
        return ""
    except Exception as exc:
        print(f"[RESPONSE AGENT] Unexpected error: {exc}")
        return ""
