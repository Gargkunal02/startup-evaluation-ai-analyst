import requests
class PerplexityService:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://api.perplexity.ai/chat/completions"

    def get_market_insights(self, query: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar",
            "messages": [{
                "role": "user",
                "content": f"Provide market insights and analysis for: {query}"
            }]
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=data
        )
        
        print(f"In PerplexityService, response: {response}")
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Perplexity API error: {response.text}")
