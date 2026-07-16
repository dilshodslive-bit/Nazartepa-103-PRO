"""Realtime WebSocket endpoint (jonli dispatch dashboard).

Brauzer WebSocket'da header yuborolmagani uchun token query parametrida
uzatiladi:  ws://host/ws/dispatch?token=<access_token>
"""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.modules.realtime.manager import manager

router = APIRouter()


@router.websocket("/ws/dispatch")
async def ws_dispatch(websocket: WebSocket, token: str | None = Query(default=None)) -> None:
    """Autentifikatsiyalangan mijozlarga jonli ambulans/dispatch voqealarini uzatadi."""
    payload = decode_token(token) if token else None
    if payload is None or payload.get("type") != "access":
        # 1008 = Policy Violation (autentifikatsiya xatosi)
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        # Server asosan yuboradi; kiruvchi xabarlarni faqat ulanishni ushlab turish
        # uchun o'qiymiz (ping/pong yoki mijoz xabarlari).
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
