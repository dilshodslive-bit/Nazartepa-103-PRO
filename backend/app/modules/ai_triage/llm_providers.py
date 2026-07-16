"""LLM asosidagi triaj provayderlari: Ollama (lokal), Anthropic, OpenAI.

Hammasi raw HTTP (httpx) orqali chaqiriladi — og'ir SDK bog'liqliklari yo'q.
Har biri prompt yuboradi, JSON javobni `parse_llm_json` bilan tekshiradi.
"""

from __future__ import annotations

import httpx

from app.modules.ai_triage.prompts import SYSTEM_PROMPT, build_user_prompt
from app.modules.ai_triage.provider import (
    AITriageProvider,
    TriageResult,
    parse_llm_json,
)

_TIMEOUT = httpx.Timeout(30.0)


class OllamaProvider(AITriageProvider):
    """Lokal LLM (Ollama). Bepul, kalitsiz — lekin server ishlab turishi kerak."""

    name = "ollama"

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def assess(self, complaint: str, *, context: str | None = None) -> TriageResult:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "stream": False,
                    "format": "json",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": build_user_prompt(complaint, context)},
                    ],
                },
            )
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
        return parse_llm_json(content, self.name)


class AnthropicProvider(AITriageProvider):
    """Anthropic Claude (Messages API, raw HTTP). API kaliti kerak."""

    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-opus-4-8") -> None:
        self.api_key = api_key
        self.model = model

    async def assess(self, complaint: str, *, context: str | None = None) -> TriageResult:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 512,
                    "system": SYSTEM_PROMPT,
                    "messages": [
                        {"role": "user", "content": build_user_prompt(complaint, context)}
                    ],
                },
            )
            resp.raise_for_status()
            # content — bloklar ro'yxati; birinchi text blokini olamiz
            blocks = resp.json()["content"]
            text = next((b["text"] for b in blocks if b.get("type") == "text"), "")
        return parse_llm_json(text, self.name)


class OpenAIProvider(AITriageProvider):
    """OpenAI Chat Completions (raw HTTP). API kaliti kerak."""

    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model

    async def assess(self, complaint: str, *, context: str | None = None) -> TriageResult:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": build_user_prompt(complaint, context)},
                    ],
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        return parse_llm_json(content, self.name)
