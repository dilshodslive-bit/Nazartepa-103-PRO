"""Triaj xizmati: provayderni tanlaydi va xatoda rule_based'ga qaytadi."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.core.logging import logger
from app.modules.ai_triage.llm_providers import (
    AnthropicProvider,
    OllamaProvider,
    OpenAIProvider,
)
from app.modules.ai_triage.provider import AITriageProvider, TriageResult
from app.modules.ai_triage.rule_based import RuleBasedProvider


def _build_provider() -> AITriageProvider:
    """Sozlamaga qarab provayder yaratadi; kalit yo'q bo'lsa rule_based'ga tushadi."""
    choice = settings.ai_triage_provider

    if choice == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.ollama_model)
    if choice == "anthropic":
        if settings.anthropic_api_key:
            return AnthropicProvider(settings.anthropic_api_key, settings.anthropic_model)
        logger.warning("ANTHROPIC_API_KEY yo'q — rule_based triajga qaytildi")
    if choice == "openai":
        if settings.openai_api_key:
            return OpenAIProvider(settings.openai_api_key, settings.openai_model)
        logger.warning("OPENAI_API_KEY yo'q — rule_based triajga qaytildi")

    return RuleBasedProvider()


@lru_cache
def _cached_provider() -> AITriageProvider:
    return _build_provider()


class TriageService:
    """Murojaat matnini AI orqali baholaydi. Har qanday xatoda rule_based zaxira."""

    def __init__(self, provider: AITriageProvider | None = None) -> None:
        self.provider = provider or _cached_provider()
        self._fallback = RuleBasedProvider()

    async def assess(self, complaint: str, *, context: str | None = None) -> TriageResult:
        try:
            return await self.provider.assess(complaint, context=context)
        except Exception as exc:  # provayder ishlamasa — murojaat baribir baholanadi
            logger.warning(
                f"Triaj provayderi '{self.provider.name}' xato berdi ({exc!r}); "
                "rule_based zaxira ishlatildi"
            )
            return await self._fallback.assess(complaint, context=context)
