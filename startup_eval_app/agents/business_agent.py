
from utils.gemini_client import call_agent

def analyze(text: str, meta: dict) -> dict:
    prompt = (
        "Return JSON with keys: founders_profile, financials_summary, facilities, technology, "
        "key_problems_solved (list), business_model, pitch_quality.\n"
        "Use the following description:\n" + text[:8000]
    )
    return call_agent(prompt)
