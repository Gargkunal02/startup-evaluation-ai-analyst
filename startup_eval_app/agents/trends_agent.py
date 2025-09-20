
from utils.gemini_client import call_agent

def analyze(text: str, meta: dict) -> dict:
    prompt = (
        "You track current news and trends. Return JSON: top_news (list), "
        "regulatory_watch (list), sentiment (positive|neutral|negative).\nContext:\n" + text[:4000]
    )
    return call_agent(prompt)
