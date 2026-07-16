"""RBAC testlari: rollarga bog'liq kirish nazorati."""

import pytest
from httpx import AsyncClient

from app.modules.users.models import User

PREFIX = "/api/v1"


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        f"{PREFIX}/auth/login", json={"email": email, "password": password}
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_citizen_cannot_list_users(client: AsyncClient) -> None:
    await client.post(
        f"{PREFIX}/auth/register",
        json={"email": "c@test.uz", "full_name": "Fuqaro", "password": "Secret12345"},
    )
    token = await _login(client, "c@test.uz", "Secret12345")
    resp = await client.get(f"{PREFIX}/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_users(client: AsyncClient, admin_user: User) -> None:
    token = await _login(client, "admin@test.uz", "Admin12345!")
    resp = await client.get(f"{PREFIX}/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_admin_can_create_operator(client: AsyncClient, admin_user: User) -> None:
    token = await _login(client, "admin@test.uz", "Admin12345!")
    resp = await client.post(
        f"{PREFIX}/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "operator@test.uz",
            "full_name": "Operator",
            "password": "Secret12345",
            "role": "operator",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "operator"
