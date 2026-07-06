Uber Core Stream Engine
A real-time telemetry pipeline that ingests, sequences, and caches high-frequency GPS data from a simulated vehicle fleet. It decouples continuous historical event logs from a sub-millisecond live state cache.

Live Demo: uber-core-stream-engine.streamlit.app

System Architecture
Simulator (services/simulator): Multi-threaded Python threads generating live driver coordinates. Uses driver_id partition keys to guarantee chronological message ordering per vehicle.

Broker (Redpanda / Kafka API): Highly efficient distributed log buffer that absorbs traffic spikes and tracks reader positions via offset bookmarks.

Cache (Redis): Consumer engine processes the stream, strips history, and overwrites an atomic dictionary snapshot inside RAM for sub-0.5ms lookups.

Dashboard (services/dashboard): Streamlit UI that automates background terminal processes, handles fleet KPIs, and maps vehicles live.

Quick Start
PowerShell
# 1. Spin up background Redpanda and Redis containers
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the unified automation control panel
python -m streamlit run services/dashboard/app.py
Open http://localhost:8501 to control the pipeline and view the live map tracker.

Project Structure
Plaintext
├── services/
│   ├── simulator/   # Multi-threaded telemetry producer & Dockerfile
│   ├── engine/      # Kafka consumer core & local verification scripts
│   └── dashboard/   # Unified Streamlit orchestration application
├── deployment.yaml  # Production cloud auto-scaling Kubernetes manifest
└── docker-compose.yml
