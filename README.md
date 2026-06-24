# Smart Environmental Monitor 🌡️

A real-time **AI + IoT** monitoring platform. A virtual IoT sensor streams
environmental readings (temperature, humidity, air quality) over a WebSocket to
a **FastAPI** backend, where an **Isolation Forest** machine-learning model
flags anomalies as they happen. A live, dependency-free dashboard visualizes
the stream and highlights every detected anomaly.

> Built to demonstrate an end-to-end pipeline: sensor → streaming → ML inference
> → live UI — the core loop behind predictive-maintenance and smart-monitoring
> systems, without needing physical hardware.

## Features

- **Virtual IoT sensor** — realistic readings with natural drift, noise, and
  occasional injected anomalies (`backend/simulator.py`).
- **AI anomaly detection** — an unsupervised Isolation Forest trained on normal
  operating data scores each reading in real time (`backend/detector.py`).
- **Real-time streaming** — readings are broadcast to every connected dashboard
  over a WebSocket (`/ws`).
- **Live dashboard** — a single self-contained HTML file (vanilla JS, custom
  canvas chart, no external libraries or build step), with current-value cards,
  a live chart, and an event feed that highlights anomalies (`frontend/index.html`).
- **REST API** — `GET /api/readings`, `GET /api/health`.

## Tech stack

| Layer      | Tech                                  |
|------------|---------------------------------------|
| Backend    | Python, FastAPI, WebSockets           |
| AI / ML    | scikit-learn (Isolation Forest), NumPy|
| Frontend   | Vanilla JS, HTML Canvas (zero deps)   |
| IoT        | Simulated sensor (MQTT-ready design)  |

## Run it

### Quick start (Windows)

```powershell
./start.ps1
```

Then open **http://127.0.0.1:8000**.

### Manual

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000 — the dashboard connects automatically and data
starts streaming within a couple of seconds.

## How it works

1. On startup, the Isolation Forest is trained on ~2000 synthetic "normal"
   samples.
2. A background task reads the simulated sensor every 2 seconds.
3. Each reading is scored by the model; anomalies get a confidence value.
4. Results are stored in a rolling 120-point history and pushed to all
   connected dashboards over the WebSocket.

## Next steps / extending

- Swap the simulator for a real device by publishing readings to **MQTT** and
  subscribing in `app.py`.
- Persist history to a database (SQLite / TimescaleDB).
- Add email/Telegram alerts when an anomaly is detected.

---

Built by **Zakaria Ould Miloud** — Master 2 Computer Science (AI & IoT).
