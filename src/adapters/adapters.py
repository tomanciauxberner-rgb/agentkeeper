from abc import ABC, abstractmethod
from src.cso.types import Fact


class BaseAdapter(ABC):
    @abstractmethod
    def query(self, system_prompt: str, user_message: str) -> str:
        pass

    def extract_facts_from_response(self, response: str, expected_facts: list[Fact]) -> list[str]:
        """Check which fact contents appear in the model response."""
        found = []
        response_lower = response.lower()
        for fact in expected_facts:
            if ":" in fact.content:
                key, value = fact.content.split(":", 1)
                keywords = [w for w in value.strip().lower().split() if len(w) > 3]
                if keywords and any(kw in response_lower for kw in keywords):
                    found.append(fact.id)
            else:
                if fact.content.lower() in response_lower:
                    found.append(fact.id)
        return found


class OpenAIAdapter(BaseAdapter):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def query(self, system_prompt: str, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content


class AnthropicAdapter(BaseAdapter):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def query(self, system_prompt: str, user_message: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text


class MockAdapter(BaseAdapter):
    def __init__(self, recall_rate: float = 1.0):
        self.recall_rate = recall_rate
        self._last_system_prompt = ""

    def query(self, system_prompt: str, user_message: str) -> str:
        self._last_system_prompt = system_prompt
        return f"Based on my memory: {system_prompt}"


class GeminiAdapter(BaseAdapter):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def query(self, system_prompt: str, user_message: str) -> str:
        response = self.model.generate_content(f"{system_prompt}\n\n{user_message}")
        return response.text


class OllamaAdapter(BaseAdapter):
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def query(self, system_prompt: str, user_message: str) -> str:
        import urllib.request, json
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False
        }).encode()
        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["message"]["content"]
