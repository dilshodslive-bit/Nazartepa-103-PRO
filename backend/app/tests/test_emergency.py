"""Emergency Call testlari: yaratish, RBAC, status oqimi va audit."""

import pytest
from httpx import AsyncClient

from app.modules.users.models import User

PREFIX = "/api/v1"


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        f"{PREFIX}/auth/login", json={"email": email, "password": password}
    )
    return resp.json()["access_token"]


async def _citizen_token(client: AsyncClient) -> str:
    await client.post(
        f"{PREFIX}/auth/register",
        json={"email": "c@test.uz", "full_name": "Fuqaro", "password": "Secret12345"},
    )
    return await _login(client, "c@test.uz", "Secret12345")


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


_CALL_PAYLOAD = {
    "caller_phone": "+998901234567",
    "caller_name": "Ali",
    "address_text": "Toshkent, Chilonzor 5",
    "latitude": 41.3,
    "longitude": 69.2,
    "complaint": "Ko'krak qafasida kuchli og'riq, nafas qisilyapti",
}


@pytest.mark.asyncio
async def test_citizen_can_create_call(client: AsyncClient) -> None:
    token = await _citizen_token(client)
    resp = await client.post(f"{PREFIX}/calls", headers=_auth(token), json=_CALL_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "new"
    assert body["priority"] is None
    assert body["media_urls"] == []
    assert body["created_by_id"] is not None


@pytest.mark.asyncio
async def test_unauthenticated_cannot_create_call(client: AsyncClient) -> None:
    resp = await client.post(f"{PREFIX}/calls", json=_CALL_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_citizen_cannot_list_calls(client: AsyncClient) -> None:
    token = await _citizen_token(client)
    resp = await client.get(f"{PREFIX}/calls", headers=_auth(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_calls(client: AsyncClient, admin_user: User) -> None:
    ctoken = await _citizen_token(client)
    await client.post(f"{PREFIX}/calls", headers=_auth(ctoken), json=_CALL_PAYLOAD)

    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    resp = await client.get(f"{PREFIX}/calls", headers=_auth(atoken))
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_status_flow_and_audit(client: AsyncClient, admin_user: User) -> None:
    ctoken = await _citizen_token(client)
    created = await client.post(
        f"{PREFIX}/calls", headers=_auth(ctoken), json=_CALL_PAYLOAD
    )
    call_id = created.json()["id"]

    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    for nxt in ("triaged", "dispatched", "en_route", "on_scene", "completed"):
        resp = await client.patch(
            f"{PREFIX}/calls/{call_id}/status",
            headers=_auth(atoken),
            json={"status": nxt},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == nxt

    # Audit: yaratish + 5 o'tish = 6 hodisa
    events = await client.get(
        f"{PREFIX}/calls/{call_id}/events", headers=_auth(atoken)
    )
    assert events.status_code == 200
    data = events.json()
    assert len(data) == 6
    assert data[0]["to_status"] == "new"
    assert data[-1]["to_status"] == "completed"
    assert data[-1]["actor_id"] == admin_user.id


@pytest.mark.asyncio
async def test_invalid_transition_rejected(client: AsyncClient, admin_user: User) -> None:
    ctoken = await _citizen_token(client)
    created = await client.post(
        f"{PREFIX}/calls", headers=_auth(ctoken), json=_CALL_PAYLOAD
    )
    call_id = created.json()["id"]

    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    # new → on_scene sakrash mumkin emas
    resp = await client.patch(
        f"{PREFIX}/calls/{call_id}/status",
        headers=_auth(atoken),
        json={"status": "on_scene"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_filter_by_status(client: AsyncClient, admin_user: User) -> None:
    ctoken = await _citizen_token(client)
    await client.post(f"{PREFIX}/calls", headers=_auth(ctoken), json=_CALL_PAYLOAD)

    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    resp = await client.get(
        f"{PREFIX}/calls", headers=_auth(atoken), params={"status": "completed"}
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
