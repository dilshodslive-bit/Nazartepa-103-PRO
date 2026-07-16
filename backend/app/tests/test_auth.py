"""Auth oqimi testlari: register, login, refresh rotation, brute-force."""

import pytest
from httpx import AsyncClient

PREFIX = "/api/v1"


async def _register(client: AsyncClient, email: str = "citizen@test.uz") -> dict:
    resp = await client.post(
        f"{PREFIX}/auth/register",
        json={"email": email, "full_name": "Test Citizen", "password": "Secret12345"},
    )
    return resp.json() | {"_status": resp.status_code}


@pytest.mark.asyncio
async def test_register_creates_citizen(client: AsyncClient) -> None:
    data = await _register(client)
    assert data["_status"] == 201
    assert data["email"] == "citizen@test.uz"
    assert data["role"] == "citizen"


@pytest.mark.asyncio
async def test_login_returns_tokens_and_user(client: AsyncClient) -> None:
    await _register(client)
    resp = await client.post(
        f"{PREFIX}/auth/login",
        json={"email": "citizen@test.uz", "password": "Secret12345"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] and body["refresh_token"]
    assert body["user"]["email"] == "citizen@test.uz"


@pytest.mark.asyncio
async def test_me_requires_valid_token(client: AsyncClient) -> None:
    await _register(client)
    login = await client.post(
        f"{PREFIX}/auth/login",
        json={"email": "citizen@test.uz", "password": "Secret12345"},
    )
    token = login.json()["access_token"]
    resp = await client.get(f"{PREFIX}/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "citizen@test.uz"

    # Tokensiz → 401
    assert (await client.get(f"{PREFIX}/users/me")).status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotation_revokes_old_token(client: AsyncClient) -> None:
    await _register(client)
    login = await client.post(
        f"{PREFIX}/auth/login",
        json={"email": "citizen@test.uz", "password": "Secret12345"},
    )
    old_refresh = login.json()["refresh_token"]

    # 1-marta refresh → yangi juftlik
    r1 = await client.post(f"{PREFIX}/auth/refresh", json={"refresh_token": old_refresh})
    assert r1.status_code == 200

    # Eski refresh qayta ishlatilsa → 401 (rotatsiya)
    r2 = await client.post(f"{PREFIX}/auth/refresh", json={"refresh_token": old_refresh})
    assert r2.status_code == 401


@pytest.mark.asyncio
async def test_wrong_password_rejected(client: AsyncClient) -> None:
    await _register(client)
    resp = await client.post(
        f"{PREFIX}/auth/login",
        json={"email": "citizen@test.uz", "password": "WrongPass999"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_brute_force_lockout(client: AsyncClient) -> None:
    await _register(client)
    # 5 xato urinish
    for _ in range(5):
        await client.post(
            f"{PREFIX}/auth/login",
            json={"email": "citizen@test.uz", "password": "bad"},
        )
    # 6-urinish (hatto to'g'ri parol bilan ham) → 429
    resp = await client.post(
        f"{PREFIX}/auth/login",
        json={"email": "citizen@test.uz", "password": "Secret12345"},
    )
    assert resp.status_code == 429
