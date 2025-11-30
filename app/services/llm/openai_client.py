import asyncio

from openai import OpenAI

from app.services.llm.base import LLMClient


class OpenAILLMClient(LLMClient):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def generate(self, prompt: str) -> str:
        return await asyncio.to_thread(self._generate, prompt)

    def _generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers using provided context and always cites sources with [n] markers."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
