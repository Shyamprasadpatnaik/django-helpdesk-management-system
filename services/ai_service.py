import os
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are the JK Paper Mill Intelligent Support Assistant.
Your goal is to guide mill employees through preliminary troubleshooting of common workplace, IT, and plant maintenance issues before they create a formal ticket.

CRITICAL SAFETY & GOVERNANCE RULES:
1. You are an advisory assistant ONLY. You CANNOT mutate ticket status, assign technicians, or close tickets.
2. For high-voltage electrical, boiler, chemical, fire hazard, or heavy spinning machinery emergencies, immediately instruct the employee to activate plant emergency stops and contact the Safety/Maintenance desk immediately.
3. Keep answers concise, clear, and structured (steps with bullet points).
4. Always conclude your advice with a recommendation on which department to submit a ticket to (e.g. IT, Electrical, Mechanical, Production) if the preliminary checks do not solve the problem.
"""

# Fallback smart triage engine when API key is not configured or network fails
FALLBACK_TRIAGE_KNOWLEDGE = {
    'printer': {
        'reply': "For paper jams: 1) Open front and rear access doors. 2) Gently pull out stuck paper in direction of feed. 3) Inspect rollers for torn scraps. If rollers are worn or jam persists, create an IT / Helpdesk ticket.",
        'suggested_dept': 'IT',
        'suggested_category': 'Printer problem'
    },
    'paper machine': {
        'reply': "For paper machine operational hiccups: 1) Check felt tension and lubrication pressure on console. 2) Inspect headbox stock consistency sensors. For sudden drive motor stops or hydraulic drop, contact the Shift Incharge immediately and file a Production/Mechanical ticket.",
        'suggested_dept': 'Production',
        'suggested_category': 'Production equipment'
    },
    'motor': {
        'reply': "Motor tripping issue: 1) Do NOT repeatedly reset thermal overload relays. 2) Check if motor casing is overheating or abnormal vibration is detected. 3) Request an Electrical technician inspection.",
        'suggested_dept': 'Electrical',
        'suggested_category': 'Machine problem'
    },
    'network': {
        'reply': "Network connectivity loss: 1) Check if the Ethernet cable is securely seated (link light flashing). 2) Restart local switch port or workstation network adapter. 3) Verify if other units in your control room have access. If disconnected plant-wide, raise an IT ticket.",
        'suggested_dept': 'IT',
        'suggested_category': 'Network problem'
    },
    'leak': {
        'reply': "Fluid/hydraulic leakage: 1) Identify fluid type (steam, water, hydraulic oil, black liquor). 2) Cordone off the area if slippery. 3) Report to Mechanical Maintenance immediately.",
        'suggested_dept': 'Maintenance',
        'suggested_category': 'Equipment problem'
    },
    'safety': {
        'reply': "SAFETY PRIORITY: In case of hazardous chemical release, smoke, or fire, sound the plant alarm, evacuate to the designated assembly zone, and notify Emergency Security directly.",
        'suggested_dept': 'Safety',
        'suggested_category': 'Safety issue'
    },
}

def generate_ai_response(user_message, conversation_history=None):
    """
    Modular AI dispatcher supporting Google Gemini, OpenAI-compatible, Groq,
    and a local industrial fallback triage engine.
    """
    provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()
    api_key = getattr(settings, 'AI_API_KEY', '').strip()
    model = getattr(settings, 'AI_MODEL', 'gemini-1.5-flash')

    # Try live API if API key is present
    if api_key and api_key != 'your_gemini_or_openai_api_key_here':
        try:
            if provider == 'gemini':
                return _call_gemini_api(api_key, model, user_message, conversation_history)
            elif provider in ('openai', 'groq'):
                return _call_openai_compatible_api(provider, api_key, model, user_message, conversation_history)
        except Exception as e:
            logger.error(f"Live AI API call failed ({provider}): {str(e)}")

    # Intelligent fallback when offline or no API key configured
    return _rule_based_fallback(user_message)


def _call_gemini_api(api_key, model, user_message, conversation_history):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    contents = []
    # Add system guidance as first user/model exchange or system instruction
    if conversation_history:
        for turn in conversation_history[-6:]:
            role = "user" if turn.get('role') == 'user' else "model"
            contents.append({"role": role, "parts": [{"text": turn.get('content', '')}]})

    contents.append({"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\nEmployee Query: {user_message}"}]})

    payload = {"contents": contents}
    response = requests.post(url, headers=headers, json=payload, timeout=12)

    if response.status_code == 200:
        data = response.json()
        candidates = data.get('candidates', [])
        if candidates:
            reply = candidates[0]['content']['parts'][0]['text']
            return {
                'success': True,
                'reply': reply,
                'provider': 'Google Gemini'
            }

    logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
    return _rule_based_fallback(user_message)


def _call_openai_compatible_api(provider, api_key, model, user_message, conversation_history):
    endpoint = "https://api.openai.com/v1/chat/completions" if provider == 'openai' else "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        for turn in conversation_history[-6:]:
            messages.append({"role": turn.get('role', 'user'), "content": turn.get('content', '')})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model or ("gpt-4o-mini" if provider == 'openai' else "llama-3.1-8b-instant"),
        "messages": messages,
        "temperature": 0.4
    }

    response = requests.post(endpoint, headers=headers, json=payload, timeout=12)
    if response.status_code == 200:
        data = response.json()
        reply = data['choices'][0]['message']['content']
        return {
            'success': True,
            'reply': reply,
            'provider': provider.capitalize()
        }

    logger.warning(f"{provider} API returned status {response.status_code}: {response.text}")
    return _rule_based_fallback(user_message)


def _rule_based_fallback(user_message):
    """
    Intelligent triage engine for JK Paper Mill when external AI API is offline.
    """
    msg_lower = user_message.lower()

    for key, data in FALLBACK_TRIAGE_KNOWLEDGE.items():
        if key in msg_lower:
            return {
                'success': True,
                'reply': data['reply'],
                'suggested_dept': data.get('suggested_dept'),
                'suggested_category': data.get('suggested_category'),
                'provider': 'JK Paper Mill Assistant (Offline Mode)'
            }

    # General fallback
    return {
        'success': True,
        'reply': (
            "I have analyzed your query. For best resolution, please ensure you check physical power and basic connectivity. "
            "If the issue persists, I recommend creating a formal support ticket with photos or error details so the relevant department technician can inspect it."
        ),
        'provider': 'JK Paper Mill Assistant (Offline Mode)'
    }
