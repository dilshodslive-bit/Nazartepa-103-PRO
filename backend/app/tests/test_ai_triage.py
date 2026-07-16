"""AI triaj testlari: rule_based provayder va murojaat bilan integratsiya."""

import pytest
from httpx import AsyncClient

from app.modules.ai_triage.rule_based import RuleBasedProvider
from app.modules.emergency.models import Priority
from app.modules.users.models import User

PREFIX = "/api/v1"


# --- Rule-based provayder (to'g'ridan-to'g'ri) ---


@pytest.mark.asyncio
async def test_rule_based_red_cardiac() -> None:
    result = await RuleBasedProvider().assess(
        "Ko'krak qafasida kuchli og'riq, nafas qisilyapti"
    )
    assert result.priority == Priority.RED
    assert result.recommended_brigade == "kardiologiya"
    assert result.severity >= 8
    assert result.provider == "rule_based"


@pytest.mark.asyncio
async def test_rule_based_yellow() -> None:
    result = await RuleBasedProvider().assess("Oyog'i singan, qattiq og'riq bor")
    assert result.priority == Priority.YELLOW
    assert result.recommended_brigade == "travmatologiya"


@pytest.mark.asyncio
async def test_rule_based_green_default() -> None:
    result = await RuleBasedProvider().assess("Yengil bosh og'rig'i, harorat normal")
    assert result.priority == Priority.GREEN
    assert result.confidence < 0.5  # kalit so'z yo'q — past ishonch


# --- Murojaat bilan integratsiya ---


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        f"{PREFIX}/auth/login", json={"email": email, "password": password}
    )
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _citizen_token(client: AsyncClient) -> str:
    await client.post(
        f"{PREFIX}/auth/register",
        json={"email": "c@test.uz", "full_name": "Fuqaro", "password": "Secret12345"},
    )
    return await _login(client, "c@test.uz", "Secret12345")


@pytest.mark.asyncio
async def test_auto_triage_on_create(client: AsyncClient) -> None:
    token = await _citizen_token(client)
    resp = await client.post(
        f"{PREFIX}/calls",
        headers=_auth(token),
        json={"caller_phone": "+998901112233", "complaint": "Insult, chap tomoni falaj"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["priority"] == "red"
    assert body["priority_source"] == "ai"
    assert body["ai_recommended_brigade"] == "nevrologiya"
    assert body["ai_reason"]


@pytest.mark.asyncio
async def test_manual_override_preserved_on_retriage(
    client: AsyncClient, admin_user: User
) -> None:
    ctoken = await _citizen_token(client)
    created = await client.post(
        f"{PREFIX}/calls",
        headers=_auth(ctoken),
        json={"caller_phone": "+998901112233", "complaint": "Yurak urishi to'xtadi"},
    )
    assert created.json()["priority"] == "red"  # AI red deb baholadi

    call_id = created.json()["id"]

    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    # Operator ustuvorlikni qo'lda "green" ga o'zgartiradi (AI red desa ham)
    upd = await client.patch(
        f"{PREFIX}/calls/{call_id}",
        headers=_auth(atoken),
        json={"priority": "green"},
    )
    assert upd.json()["priority"] == "green"
    assert upd.json()["priority_source"] == "manual"

    # Qayta triaj: AI maydonlari yangilanadi, lekin qo'lda ustuvorlik saqlanadi
    retr = await client.post(f"{PREFIX}/calls/{call_id}/triage", headers=_auth(atoken))
    assert retr.status_code == 200
    body = retr.json()
    assert body["priority"] == "green"  # qo'lda tanlov saqlandi
    assert body["priority_source"] == "manual"
    assert body["ai_provider"] == "rule_based"  # AI baribir baholadi


@pytest.mark.asyncio
async def test_citizen_cannot_retriage(client: AsyncClient) -> None:
    token = await _citizen_token(client)
    created = await client.post(
        f"{PREFIX}/calls",
        headers=_auth(token),
        json={"caller_phone": "+998901112233", "complaint": "Bosh og'rig'i"},
    )
    call_id = created.json()["id"]
    resp = await client.post(f"{PREFIX}/calls/{call_id}/triage", headers=_auth(token))
    assert resp.status_code == 403
