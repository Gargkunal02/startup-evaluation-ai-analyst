
import os, json

def _try_gemini_generate(system_prompt: str, user_prompt: str) -> str:
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content([
            {"role": "system", "parts": [system_prompt]},
            {"role": "user", "parts": [user_prompt]}
        ])
        return res.text or ""
    except Exception:
        return "{\"note\": \"fallback\", \"detail\": \"Gemini not configured\"}"

def call_agent(prompt: str) -> dict:
    system = "You are a precise startup evaluation agent. Return JSON only."
    out = _try_gemini_generate(system, prompt)
    # try parse JSON
    try:
        s = out.strip().strip("`")
        if s.lower().startswith("json"):
            s = s[4:].strip()
        return json.loads(s)
    except Exception:
        return {"raw": out}
