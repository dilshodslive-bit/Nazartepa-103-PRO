"""AI triaj provayder abstraktsiyasi (provayderdan mustaqil).

Har provayder `assess(complaint)` ni bajarib, standart `TriageResult` qaytaradi.
Bu qatlam tufayli murojaat mantiqiga tegmasdan rule_based / ollama / anthropic /
openai o'rtasida almashtirish mumkin.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from app.modules.emergency.models import Priority


class TriageResult(BaseModel):
    """AI triaj natijasi — standart chiqish shakli."""

    priority: Priority
    severity: int = Field(ge=1, le=10, description="Og'irlik darajasi (1=yengil, 10=kritik)")
    recommended_brigade: str = Field(
        max_length=64, description="Tavsiya etilgan brigada turi"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Ishonchlilik (0..1)")
    reason: str = Field(max_length=512, description="Qisqa izoh (operator uchun)")
    provider: str = Field(max_length=32, description="Natijani bergan provayder")


class AITriageProvider(ABC):
    """Barcha triaj provayderlari uchun umumiy interfeys."""

    name: str = "base"

    @abstractmethod
    async def assess(self, complaint: str, *, context: str | None = None) -> TriageResult:
        """Shikoyat matnini baholab, TriageResult qaytaradi."""
        raise NotImplementedError


# --- LLM provayderlari uchun umumiy yordamchilar ---

_VALID_BRIGADES = {
    "reanimatsiya",
    "kardiologiya",
    "travmatologiya",
    "nevrologiya",
    "pediatriya",
    "umumiy",
}


def parse_llm_json(raw: str, provider: str) -> TriageResult:
    """LLM javobidagi JSON'ni TriageResult'ga aylantiradi (himoyalangan)."""
    text = raw.strip()
    # Markdown ```json ... ``` ramkasini olib tashlash
    if text.startswith("```"):
        text = text.split("```")[1] if "```" in text[3:] else text.strip("`")
        text = text.removeprefix("json").strip()
    # Faqat birinchi { ... } bloki
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]

    data = json.loads(text)
    priority = Priority(str(data["priority"]).lower())
    brigade = str(data.get("recommended_brigade", "umumiy")).lower().strip()
    if brigade not in _VALID_BRIGADES:
        brigade = "umumiy"
    return TriageResult(
        priority=priority,
        severity=int(data.get("severity", 5)),
        recommended_brigade=brigade,
        confidence=float(data.get("confidence", 0.7)),
        reason=str(data.get("reason", ""))[:512],
        provider=provider,
    )
