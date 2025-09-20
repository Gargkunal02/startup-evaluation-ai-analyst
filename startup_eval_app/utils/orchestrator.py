
from agents import industry_agent, business_agent, funding_agent, timing_agent, trends_agent

def _score(outputs: dict) -> dict:
    reasons = []
    score = 0
    if outputs.get("business", {}).get("technology"): 
        score += 1; reasons.append("Clear technology description")
    if outputs.get("business", {}).get("business_model"):
        score += 1; reasons.append("Defined business model")
    if outputs.get("industry", {}).get("competitor_framework"):
        score += 1; reasons.append("Competitor analysis present")
    if outputs.get("timing", {}).get("market_trends"):
        score += 1; reasons.append("Favorable market trends")
    if outputs.get("trends", {}).get("sentiment") == "positive":
        score += 1; reasons.append("Positive news sentiment")
    if outputs.get("funding", {}).get("valuation"):
        score += 1; reasons.append("Reported valuation & round structure")
    return {"is_good": score >= 4, "top_reasons": reasons[:5], "score": score}

def run_multi_agent_analysis(startup: dict) -> dict:
    text = startup.get("description", "")
    out = {
        "industry": industry_agent.analyze(text, startup),
        "business": business_agent.analyze(text, startup),
        "funding": funding_agent.analyze(text, startup),
        "timing": timing_agent.analyze(text, startup),
        "trends": trends_agent.analyze(text, startup),
    }
    out.update(_score(out))
    return out
