
from utils.gemini_client import call_agent

def analyze(text: str, meta: dict) -> dict:
    prompt = (
        "Return JSON with keys: market_trends (list), competitive_edge, technical_insight, "
        "opportunity_urgency, risks_and_mitigation (list).\nGiven:\n" + text[:8000]
    )
    return call_agent(prompt)
