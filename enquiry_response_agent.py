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
        f"Tone and style: {voice_profile}\n\n"

        "## Your job\n"
        "Generate a first response to an inbound lead. The goal is one thing: move the prospect "
        "toward a call or site visit. Not to close the job. Not to quote. Not to commit to anything.\n\n"

        "## Hard rules — never break these\n"
        "1. Never quote a price. If a budget is mentioned, do not agree to it, reject it, or reference "
        "it as a number. Acknowledge that pricing depends on the details and redirect to a conversation.\n"
        "2. Never confirm availability. Do not say 'we can do Tuesday' or 'we're free next week.' "
        "Frame timing as something to discuss once the details are clearer.\n"
        "3. Never agree to scope without details. Do not say 'yes we can do that' until you know "
        "what that actually involves.\n"
        "4. Never accept a low budget and agree to work anyway. Ask questions that surface the full "
        "scope before any commitment is implied.\n"
        "5. Never make promises about outcomes, timelines, or guarantees.\n\n"

        "## What every response must do\n"
        "1. Acknowledge the enquiry warmly. One sentence. Make the prospect feel heard.\n"
        "2. Ask 1 to 2 qualifying questions. Pick the most important unknowns. Never ask more than two at once.\n"
        "3. Signal the next step. End with a clear, low-friction action: a call, a quick chat, or a "
        "site visit. Never leave the response open-ended.\n\n"

        "## Qualifying questions to draw from (pick the most relevant)\n"
        "- What exactly needs doing? (scope)\n"
        "- Whereabouts are you located? (service area check)\n"
        "- Is this urgent or a planned project? (timeline)\n"
        "- How big is the area / what scale are we talking? (scope sizing)\n"
        "- Have you had anyone else look at it yet? (buying journey)\n"
        "- Is there anything about the job that might be tricky to access? (complications)\n\n"

        "## Tone rules\n"
        "- Warm, direct, conversational. Write like a trusted local tradesperson, not a corporate call centre.\n"
        "- Short paragraphs. Two to three sentences max per block.\n"
        "- No jargon without explanation.\n"
        "- Never say 'as per your enquiry', 'please do not hesitate', or similar corporate filler.\n"
        "- Never use em dashes (—) or hyphens (-) as punctuation anywhere in the response. Replace with a comma, colon, period, or a connecting word like 'and', 'but', or 'so'. No exceptions.\n\n"

        "## Response structure\n"
        "[Warm acknowledgement of what they need — 1 sentence]\n\n"
        "[Qualifying question 1]\n\n"
        "[Qualifying question 2 if needed]\n\n"
        "[Soft next step — offer a call or quick chat to get the details right]"
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
