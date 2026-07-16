"""Geografik yordamchilar: masofa va ETA hisoblash."""

from __future__ import annotations

import math

# O'rtacha shahar tezligi (km/soat) — ETA taxminini hisoblash uchun
AVG_SPEED_KMH = 40.0
EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Ikki koordinata orasidagi masofa (km), haversine formulasi bo'yicha."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def eta_minutes(distance_km: float, speed_kmh: float = AVG_SPEED_KMH) -> int:
    """Masofadan taxminiy yetib borish vaqti (daqiqa, kamida 1)."""
    if speed_kmh <= 0:
        return 1
    return max(1, round(distance_km / speed_kmh * 60))
