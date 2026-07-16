"""M4 testlari: ambulance, dispatch (eng yaqin/brigada afzalligi) va realtime WS."""

import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.security import create_access_token
from app.main import app
from app.modules.realtime.manager import ConnectionManager
from app.modules.users.models import User

PREFIX = "/api/v1"


# ============ Yordamchilar ============


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


async def _make_ambulance(client, token, callsign, lat, lng, brigade="umumiy"):
    resp = await client.post(
        f"{PREFIX}/ambulances",
        headers=_auth(token),
        json={
            "callsign": callsign,
            "brigade_type": brigade,
            "latitude": lat,
            "longitude": lng,
        },
    )
    return resp


async def _make_call(client, token, lat, lng, complaint="Yiqilib tushdi"):
    resp = await client.post(
        f"{PREFIX}/calls",
        headers=_auth(token),
        json={
            "caller_phone": "+998901112233",
            "latitude": lat,
            "longitude": lng,
            "complaint": complaint,
        },
    )
    return resp.json()["id"]


# ============ Ambulance CRUD + RBAC ============


@pytest.mark.asyncio
async def test_citizen_cannot_create_ambulance(client: AsyncClient) -> None:
    token = await _citizen_token(client)
    resp = await _make_ambulance(client, token, "103-99", 41.3, 69.2)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_creates_and_lists_ambulance(
    client: AsyncClient, admin_user: User
) -> None:
    token = await _login(client, "admin@test.uz", "Admin12345!")
    resp = await _make_ambulance(client, token, "103-01", 41.31, 69.24)
    assert resp.status_code == 201
    assert resp.json()["status"] == "available"

    lst = await client.get(f"{PREFIX}/ambulances", headers=_auth(token))
    assert lst.status_code == 200
    assert lst.json()["total"] == 1


@pytest.mark.asyncio
async def test_duplicate_callsign_conflict(client: AsyncClient, admin_user: User) -> None:
    token = await _login(client, "admin@test.uz", "Admin12345!")
    await _make_ambulance(client, token, "103-01", 41.31, 69.24)
    dup = await _make_ambulance(client, token, "103-01", 41.5, 69.5)
    assert dup.status_code == 409


@pytest.mark.asyncio
async def test_location_update(client: AsyncClient, admin_user: User) -> None:
    token = await _login(client, "admin@test.uz", "Admin12345!")
    created = await _make_ambulance(client, token, "103-01", 41.31, 69.24)
    amb_id = created.json()["id"]
    resp = await client.patch(
        f"{PREFIX}/ambulances/{amb_id}/location",
        headers=_auth(token),
        json={"latitude": 41.4, "longitude": 69.3},
    )
    assert resp.status_code == 200
    assert resp.json()["latitude"] == 41.4
    assert resp.json()["last_location_at"] is not None


# ============ Dispatch: eng yaqin brigada ============


@pytest.mark.asyncio
async def test_dispatch_picks_nearest(client: AsyncClient, admin_user: User) -> None:
    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    ctoken = await _citizen_token(client)

    near = (await _make_ambulance(client, atoken, "103-01", 41.305, 69.245)).json()
    far = (await _make_ambulance(client, atoken, "103-02", 41.90, 69.90)).json()

    call_id = await _make_call(client, ctoken, 41.30, 69.24)
    # new -> triaged (tayinlashdan oldin kerak)
    await client.patch(
        f"{PREFIX}/calls/{call_id}/status", headers=_auth(atoken),
        json={"status": "triaged"},
    )

    disp = await client.post(
        f"{PREFIX}/calls/{call_id}/dispatch", headers=_auth(atoken), json={}
    )
    assert disp.status_code == 201, disp.text
    body = disp.json()
    assert body["ambulance_id"] == near["id"]  # yaqinrog'i tanlandi
    assert body["ambulance_id"] != far["id"]
    assert body["eta_minutes"] >= 1
    assert body["distance_km"] < 5

    # Brigada band bo'ldi
    amb = await client.get(f"{PREFIX}/ambulances/{near['id']}", headers=_auth(atoken))
    assert amb.json()["status"] == "dispatched"
    assert amb.json()["current_call_id"] == call_id

    # Murojaat dispatched holatiga o'tdi
    c = await client.get(f"{PREFIX}/calls/{call_id}", headers=_auth(atoken))
    assert c.json()["status"] == "dispatched"


@pytest.mark.asyncio
async def test_dispatch_prefers_matching_brigade(
    client: AsyncClient, admin_user: User
) -> None:
    """AI kardiologiya tavsiya qilsa — uzoqroq bo'lsa ham kardiologiya brigadasi."""
    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    ctoken = await _citizen_token(client)

    # Yaqinroq umumiy va uzoqroq kardiologiya
    near_general = (
        await _make_ambulance(client, atoken, "103-01", 41.301, 69.241, "umumiy")
    ).json()
    far_cardio = (
        await _make_ambulance(client, atoken, "103-02", 41.33, 69.27, "kardiologiya")
    ).json()

    call_id = await _make_call(
        client, ctoken, 41.30, 69.24, complaint="Yurak sanchishi, ko'krak og'riq"
    )
    await client.patch(
        f"{PREFIX}/calls/{call_id}/status", headers=_auth(atoken),
        json={"status": "triaged"},
    )
    disp = await client.post(
        f"{PREFIX}/calls/{call_id}/dispatch", headers=_auth(atoken), json={}
    )
    assert disp.status_code == 201, disp.text
    # Uzoqroq bo'lsa ham kardiologiya brigadasi tanlandi
    assert disp.json()["ambulance_id"] == far_cardio["id"]
    assert disp.json()["ambulance_id"] != near_general["id"]


@pytest.mark.asyncio
async def test_dispatch_requires_triaged(client: AsyncClient, admin_user: User) -> None:
    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    ctoken = await _citizen_token(client)
    await _make_ambulance(client, atoken, "103-01", 41.305, 69.245)
    call_id = await _make_call(client, ctoken, 41.30, 69.24)
    # Holat hali 'new' — tayinlab bo'lmaydi
    resp = await client.post(
        f"{PREFIX}/calls/{call_id}/dispatch", headers=_auth(atoken), json={}
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_dispatch_no_available(client: AsyncClient, admin_user: User) -> None:
    atoken = await _login(client, "admin@test.uz", "Admin12345!")
    ctoken = await _citizen_token(client)
    call_id = await _make_call(client, ctoken, 41.30, 69.24)
    await client.patch(
        f"{PREFIX}/calls/{call_id}/status", headers=_auth(atoken),
        json={"status": "triaged"},
    )
    resp = await client.post(
        f"{PREFIX}/calls/{call_id}/dispatch", headers=_auth(atoken), json={}
    )
    assert resp.status_code == 409  # bo'sh brigada yo'q


# ============ Realtime WebSocket ============


class _FakeWS:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[dict] = []

    async def send_json(self, data: dict) -> None:
        if self.fail:
            raise RuntimeError("uzilgan ulanish")
        self.sent.append(data)


@pytest.mark.asyncio
async def test_connection_manager_broadcast_and_prune() -> None:
    mgr = ConnectionManager()
    good, bad = _FakeWS(), _FakeWS(fail=True)
    mgr._connections = {good, bad}
    await mgr.broadcast({"type": "test", "x": 1})
    assert good.sent == [{"type": "test", "x": 1}]
    assert bad not in mgr._connections  # uzilgan ulanish tozalandi


def test_ws_rejects_without_token() -> None:
    with TestClient(app) as tc, pytest.raises(WebSocketDisconnect):
        tc.websocket_connect("/ws/dispatch").__enter__()


def test_ws_accepts_with_valid_token() -> None:
    token, _, _ = create_access_token("1")
    with TestClient(app) as tc, tc.websocket_connect(f"/ws/dispatch?token={token}"):
        pass  # ulanish qabul qilindi (xato yo'q)
