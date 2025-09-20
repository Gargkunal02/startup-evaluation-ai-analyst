
from utils.gemini_client import call_agent

def analyze(text: str, meta: dict) -> dict:
    prompt = (
        "Return JSON with keys: "
        "market_size, revenue_streams (list), pricing_strategy, unit_economics, "
        "recurring_vs_onetime, payment_terms, scalability, extra_opportunities (list), "
        "competitor_framework.\n"
        "Given the following startup description:\n" + text[:8000]
    )
    return call_agent(prompt)
