"""Qoida asosidagi triaj — API kalitsiz, offline ishlaydi (dev default).

Kalit so'zlar orqali RED / YELLOW / GREEN va brigada turini aniqlaydi.
LLM provayderlar mavjud bo'lmaganda ishonchli zaxira (fallback) sifatida ham
ishlatiladi.
"""

from __future__ import annotations

from app.modules.ai_triage.provider import AITriageProvider, TriageResult
from app.modules.emergency.models import Priority

# --- Kalit so'z to'plamlari (o'zbekcha; kichik harfga keltirilib qidiriladi) ---

# Hayotiy xavf → RED
_RED_KEYWORDS = {
    "nafas olmayapti",
    "nafas yo'q",
    "nafas qisilyapti",
    "hushidan ketdi",
    "hushsiz",
    "es-hushi yo'q",
    "yurak to'xtadi",
    "yurak urishi to'xtadi",
    "ko'p qon",
    "qon ketyapti",
    "insult",
    "falaj",
    "og'ir jarohat",
    "avariya",
    "halokat",
    "kuchli kuyish",
    "zaharlanish",
    "og'ir tug'ruq",
    "chaqaloq tug'ilyapti",
    "elektr toki urdi",
    "cho'kib ketdi",
    "portlash",
    "o'q tegdi",
    "pichoq",
    "ko'krak qafasida kuchli og'riq",
}

# Shoshilinch, lekin barqaror → YELLOW
_YELLOW_KEYWORDS = {
    "sindi",
    "singan",
    "yiqildi",
    "yiqilib tushdi",
    "yuqori isitma",
    "qusish",
    "qattiq og'riq",
    "jarohat",
    "yuqori bosim",
    "qon bosimi",
    "og'riq",
    "shikast",
    "lat yedi",
    "allergiya",
    "hushi og'yapti",
    "bosh aylanyapti",
}

# Brigada mos kelishi (kalit so'z → brigada)
_BRIGADE_KEYWORDS = {
    "kardiologiya": {"yurak", "ko'krak", "bosim", "qon bosimi", "infarkt"},
    "nevrologiya": {"insult", "falaj", "bosh", "es-hush", "hushidan", "tutqanoq"},
    "travmatologiya": {
        "sindi",
        "singan",
        "jarohat",
        "avariya",
        "yiqildi",
        "kuyish",
        "lat",
        "shikast",
        "pichoq",
        "o'q",
    },
    "pediatriya": {"chaqaloq", "bola", "go'dak", "tug'ruq", "tug'ilyapti"},
}


def _match_brigade(text: str, priority: Priority) -> str:
    for brigade, keywords in _BRIGADE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return brigade
    return "reanimatsiya" if priority == Priority.RED else "umumiy"


class RuleBasedProvider(AITriageProvider):
    name = "rule_based"

    async def assess(self, complaint: str, *, context: str | None = None) -> TriageResult:
        text = complaint.lower()

        red_hits = [kw for kw in _RED_KEYWORDS if kw in text]
        yellow_hits = [kw for kw in _YELLOW_KEYWORDS if kw in text]

        if red_hits:
            priority = Priority.RED
            severity = 9
            confidence = 0.7
            reason = "Hayotiy xavf belgilari: " + ", ".join(red_hits[:3])
        elif yellow_hits:
            priority = Priority.YELLOW
            severity = 6
            confidence = 0.6
            reason = "Shoshilinch belgilar: " + ", ".join(yellow_hits[:3])
        else:
            priority = Priority.GREEN
            severity = 3
            confidence = 0.35  # kalit so'z topilmadi — past ishonch
            reason = "Kalit so'zlar topilmadi; standart yashil baholash"

        return TriageResult(
            priority=priority,
            severity=severity,
            recommended_brigade=_match_brigade(text, priority),
            confidence=confidence,
            reason=reason,
            provider=self.name,
        )
