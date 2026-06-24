"""Smart Environmental Monitor — FastAPI backend.

Ties everything together:
  * a background task drives the virtual sensor every few seconds,
  * each reading is scored by the AI anomaly detector,
  * results are stored in a rolling history and broadcast to every connected
    dashboard over a WebSocket,
  * the React dashboard (in ../frontend) is served as static files.

Run:  uvicorn app:app --reload   (from the backend/ folder)
"""

from __future__ import annotations

import asyncio
import json
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from detector import AnomalyDetector
from simulator import SensorSimulator

SAMPLE_INTERVAL_SECONDS = 2.0
HISTORY_SIZE = 120

simulator = SensorSimulator()
detector = AnomalyDetector()
history: deque[dict] = deque(maxlen=HISTORY_SIZE)


class ConnectionManager:
    """Tracks connected dashboards and fans out each new reading."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)
        # Send the recent history so a fresh dashboard isn't blank.
        await ws.send_text(json.dumps({"type": "history", "data": list(history)}))

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


async def sensor_loop() -> None:
    """Background producer: read sensor -> score -> store -> broadcast."""
    while True:
        reading, injected = simulator.next_reading()
        is_anomaly, confidence = detector.score(
            reading.temperature, reading.humidity, reading.aqi
        )
        record = {
            **reading.to_dict(),
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "injected": injected,
        }
        history.append(record)
        await manager.broadcast({"type": "reading", "data": record})
        await asyncio.sleep(SAMPLE_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    detector.train()
    task = asyncio.create_task(sensor_loop())
    yield
    task.cancel()


app = FastAPI(title="Smart Environmental Monitor", lifespan=lifespan)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "connected_dashboards": len(manager.active)}


@app.get("/api/readings")
async def readings() -> dict:
    return {"count": len(history), "readings": list(history)}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            # We don't expect client messages; this keeps the socket open.
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


# Serve any other static assets (kept last so it doesn't shadow the API).
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
