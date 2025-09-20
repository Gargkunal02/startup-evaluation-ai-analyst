
from utils.gemini_client import call_agent

def analyze(text: str, meta: dict) -> dict:
    prompt = (
        "Return JSON with keys: funding_history (list of {round, amount, date, investors}), "
        "current_stage, valuation, round_structure.\nBased on:\n" + text[:8000]
    )
    return call_agent(prompt)
