"""WebSocket ulanishlarini boshqaruvchi (jonli dashboard uchun).

Modul darajasidagi yagona `manager` — boshqa modullar (ambulance, dispatch)
voqealarni shu orqali barcha ulangan mijozlarga tarqatadi.
"""

from __future__ import annotations

from typing import Any

from starlette.websockets import WebSocket

from app.core.logging import logger


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)
        logger.info(f"WebSocket ulandi (jami: {len(self._connections)})")

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Xabarni barcha ulangan mijozlarga yuboradi (uzilganlarni tozalaydi)."""
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.discard(ws)

    @property
    def count(self) -> int:
        return len(self._connections)


manager = ConnectionManager()
