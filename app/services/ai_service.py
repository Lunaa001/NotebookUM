import os
import requests


class AIService:
    def __init__(self):
        self.api_key = os.environ.get("SECRET_KEY")
        self.api_url = os.environ.get("URL_API")

    def query(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {"model": "gemma3-4b", "messages": [{"role": "user", "content": prompt}]}

        response = requests.post(
            f"{self.api_url}/chat/completions", headers=headers, json=data
        )

        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
