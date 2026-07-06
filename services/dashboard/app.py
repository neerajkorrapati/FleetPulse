import json
import os
import sys
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import redis
import streamlit as st

# 1. Compute Dynamic Root Path Alignment
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# 2. Page Canvas Frame Layout
st.set_page_config(
    page_title="FleetPulse Orchestrator",
    page_icon="🎛️",
    layout="wide"
)

st.title("🎛️ Distributed Pipeline Automation Control Center")
st.markdown("---")

# 3. Persistent Global Process Manager Container with Cloud-Safe Handling
class PipelineOrchestrator:
    def __init__(self):
        self.engine_process = None
        self.simulator_process = None
        self.docker_status = "Offline"

    def boot_docker(self):
        try:
            st.toast("Spinning up background Docker nodes...", icon="🐳")
            subprocess.run(["docker", "compose", "up", "-d"], cwd=ROOT_DIR, check=True)
            self.docker_status = "Online"
            time.sleep(2)
        except (FileNotFoundError, subprocess.SubprocessError):
            self.docker_status = "Unavailable"
            st.toast("Docker CLI unavailable in this environment.", icon="⚠️")

    def shutdown_docker(self):
        try:
            st.toast("Dropping database containers...", icon="🛑")
            self.stop_engine()
            self.stop_simulator()
            subprocess.run(["docker", "compose", "down"], cwd=ROOT_DIR, check=True)
            self.docker_status = "Offline"
        except (FileNotFoundError, subprocess.SubprocessError):
            self.docker_status = "Unavailable"

    def start_engine(self):
        if not self.engine_process or self.engine_process.poll() is not None:
            script_path = os.path.join(ROOT_DIR, "services", "engine", "matching_engine.py")
            try:
                self.engine_process = subprocess.Popen([sys.executable, script_path], cwd=ROOT_DIR)
                st.toast("Asynchronous Consumer Core active.", icon="🧠")
            except FileNotFoundError:
                st.error("❌ Python engine scripts cannot be executed from this environment.")

    def stop_engine(self):
        if self.engine_process and self.engine_process.poll() is None:
            self.engine_process.terminate()
            self.engine_process.wait()
            self.engine_process = None
            st.toast("Consumer Core cleanly stopped.", icon="⏹️")

    def start_simulator(self):
        if not self.simulator_process or self.simulator_process.poll() is not None:
            script_path = os.path.join(ROOT_DIR, "services", "simulator", "driver_producer.py")
            try:
                self.simulator_process = subprocess.Popen([sys.executable, script_path], cwd=ROOT_DIR)
                st.toast("Telemetry Ingestion Thread Matrix activated.", icon="🚗")
            except FileNotFoundError:
                st.error("❌ Fleet simulator cannot be executed from this environment.")

    def stop_simulator(self):
        if self.simulator_process and self.simulator_process.poll() is None:
            self.simulator_process.terminate()
            self.simulator_process.wait()
            self.simulator_process = None
            st.toast("Telemetry Generator offline.", icon="⏹️")

# Cache the orchestrator as a resource so running processes persist across script reruns
@st.cache_resource
def get_orchestrator():
    return PipelineOrchestrator()

orchestrator = get_orchestrator()

# 4. Interactive Sidebar Process Control Matrix
st.sidebar.header("🎛️ Pipeline Automation Switches")
st.sidebar.markdown("---")

# Section A: Docker Container Lifecycle
st.sidebar.subheader("1. Container Layer")
if orchestrator.docker_status == "Unavailable":
    st.sidebar.warning("☁️ Cloud Mode Active")
    st.sidebar.caption("Docker CLI automation is disabled on Streamlit Cloud.")
elif orchestrator.docker_status == "Offline":
    st.sidebar.error("🐳 Docker Appliances: Down")
    if st.sidebar.button("Launch Docker Cluster"):
        orchestrator.boot_docker()
        st.rerun()
else:
    st.sidebar.success("🐳 Docker Appliances: Running")
    if st.sidebar.button("Teardown Docker Cluster"):
        orchestrator.shutdown_docker()
        st.rerun()

st.sidebar.markdown("---")

# Section B: Engine Processing Loop
st.sidebar.subheader("2. Matching Engine Core")
is_engine_active = orchestrator.engine_process and orchestrator.engine_process.poll() is None
if not is_engine_active:
    st.sidebar.error("🧠 Consumer Core: Stopped")
    if st.sidebar.button("Start Processing Loop", disabled=(orchestrator.docker_status in ["Offline", "Unavailable"])):
        orchestrator.start_engine()
        st.rerun()
else:
    st.sidebar.success("🧠 Consumer Core: Active")
    if st.sidebar.button("Stop Processing Loop"):
        orchestrator.stop_engine()
        st.rerun()

st.sidebar.markdown("---")

# Section C: Driver Simulation Fleet
st.sidebar.subheader("3. Fleet Ingestion Firehose")
is_sim_active = orchestrator.simulator_process and orchestrator.simulator_process.poll() is None
if not is_sim_active:
    st.sidebar.error("🚗 Driver Threads: Idle")
    if st.sidebar.button("Ignite Driver Matrix", disabled=(orchestrator.docker_status in ["Offline", "Unavailable"])):
        orchestrator.start_simulator()
        st.rerun()
else:
    st.sidebar.success("🚗 Driver Threads: Streaming")
    if st.sidebar.button("Stop Driver Matrix"):
        orchestrator.stop_simulator()
        st.rerun()

# 5. Core Operational UI Grid Evaluation Logic
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    all_drivers = redis_client.hgetall("driver:state")
except Exception:
    all_drivers = None

if orchestrator.docker_status == "Unavailable":
    st.info("☁️ **Cloud Mode Display Showcase**\n\nThe UI controls are sandboxed on Streamlit Cloud. To interactively spin up infrastructure nodes, run this orchestrator locally using `python -m streamlit run services/dashboard/app.py`.")
elif orchestrator.docker_status == "Offline" or all_drivers is None:
    st.info("🔌 System Backends are Offline. Click 'Launch Docker Cluster' in the sidebar panel to initialize your streaming environment.")
elif not all_drivers:
    st.warning("⏳ Cache Grid Initialized! Boot the Consumer Core and Ignite your Driver Matrix to populate your real-time analytics data grid.")
else:
    # Compile telemetry frames dynamically from RAM
    parsed_drivers = []
    avail, ontrip = 0, 0
    
    for d_id, data_str in all_drivers.items():
        payload = json.loads(data_str)
        status = payload.get("status", "OFFLINE")
        if status == "AVAILABLE":
            avail += 1
        elif status == "ON_TRIP":
            ontrip += 1
            
        parsed_drivers.append({
            "Driver ID": d_id,
            "latitude": float(payload.get("latitude", 0.0)),
            "longitude": float(payload.get("longitude", 0.0)),
            "Operational Status": status,
            "Last Update (UTC)": payload.get("last_updated", "")
        })
    
    df = pd.DataFrame(parsed_drivers)
    
    # Render KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Connected Vehicles", f"{len(df)} Units")
    kpi2.metric("🟢 Available Status", f"{avail} Units")
    kpi3.metric("🟡 Active Trip Status", f"{ontrip} Units")
    
    st.markdown("---")
    
    # Map & Data Grid Views
    map_col, grid_col = st.columns([2, 1])
    
    with map_col:
        st.subheader("🗺️ Live Geospatial Projection Mesh")
        st.map(df, size=40, color="#1f77b4")
        
    with grid_col:
        st.subheader("📋 In-Memory State Register")
        st.dataframe(df.sort_values("Driver ID")[["Driver ID", "Operational Status"]], hide_index=True, use_container_width=True)
        
    # Periodic screen automatic refresh trigger loop
    time.sleep(2)
    st.rerun()