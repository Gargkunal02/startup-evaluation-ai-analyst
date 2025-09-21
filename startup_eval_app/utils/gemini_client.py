import os, json
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Reduce noisy gRPC/ALTS logs when running outside GCP
os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GRPC_LOG_SEVERITY_LEVEL", "ERROR")
os.environ.setdefault("GLOG_minloglevel", "3")

def _offline_structured_response(prompt: str) -> dict:
    # \"\"\"Return a well-formed JSON with fields used by downstream scoring when Gemini isn't configured.\"\"\"
    return {
        # Industry
        "market_size": "Unknown",
        "revenue_streams": ["subscription", "services"],
        "pricing_strategy": "tiered",
        "unit_economics": "unknown",
        "recurring_vs_onetime": "mixed",
        "payment_terms": "net-30",
        "scalability": "unclear",
        "extra_opportunities": ["partnerships"],
        "competitor_framework": "basic desk research",
        # Business
        "founders_profile": "not provided",
        "financials_summary": "not available",
        "facilities": "n/a",
        "technology": "general ML stack",
        "key_problems_solved": ["automation"],
        "business_model": "SaaS",
        "pitch_quality": "draft",
        # Funding
        "funding_history": [],
        "current_stage": "seed",
        "valuation": 0,
        "round_structure": "equity",
        # Timing
        "market_trends": ["emerging interest"],
        "competitive_edge": "undifferentiated",
        "technical_insight": "n/a",
        "opportunity_urgency": "normal",
        "risks_and_mitigation": ["product-market fit risk"],
        # Trends
        "top_news": [],
        "regulatory_watch": [],
        "sentiment": "neutral",
        "_offline": True
    }

def _try_gemini_generate(system_prompt: str, user_prompt: str) -> str:
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        res = model.generate_content([
            # {"role": "system", "parts": [system_prompt]},
            {"role": "user", "parts": [user_prompt]}
        ])
        return res.text or ""
    except Exception:
        # Return JSON string for easier downstream parsing
        return json.dumps(_offline_structured_response(user_prompt))

def call_agent(prompt: str) -> dict:
    # \"\"\"Generic caller for LLM. Returns parsed JSON. Falls back to structured local defaults.\"\"\"
    system = "You are a precise startup evaluation agent. Return JSON only."
    out = _try_gemini_generate(system, prompt)
    try:
        s = out.strip().strip("`")
        if s.lower().startswith("json"):
            s = s[4:].strip()
    except Exception:
        # Last resort: ensure we always return structured dict
        return _offline_structured_response(prompt)


