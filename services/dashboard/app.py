import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import redis
import streamlit as st

# Load environment configuration from the root directory
load_dotenv(dotenv_path="../../.env")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# 1. Page Configuration Framework
st.set_page_config(
    page_title="Uber Core Stream Engine Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚗 Core Stream Telemetry & State Grid Monitor")
st.markdown("---")

# 2. Cached Connection Pool to Redis RAM Grid
@st.cache_resource
def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

try:
    redis_client = get_redis_client()
except Exception as e:
    st.error(f"Failed to connect to Redis State Grid: {str(e)}")

# 3. Sidebar Pipeline Control Layer
st.sidebar.header("⚙️ Pipeline Controls")
auto_refresh = st.sidebar.checkbox("Enable Live Engine Tracking", value=True)
refresh_interval = st.sidebar.slider("Refresh Frequency (seconds)", 1, 5, 2)

st.sidebar.markdown("---")
st.sidebar.markdown("### System Architecture Status")
st.sidebar.success("📡 Ingestion Bridge: Online")
st.sidebar.success("🧠 Consumer Matching Engine: Online")
st.sidebar.success("⚡ In-Memory Cache Grid: Online")

# 4. Infinite View Loop for Real-Time State Rendering
view_container = st.empty()

while True:
    with view_container.container():
        # Fetch the complete real-time dictionary frame out of Redis RAM
        all_drivers = redis_client.hgetall("driver:state")
        
        if not all_drivers:
            st.info("⏳ Waiting for active telemetry records to hit the Redis grid... Start your driver simulation engine.")
        else:
            # Process and parse raw strings into a clean dataset array
            parsed_drivers = []
            available_count = 0
            ontrip_count = 0
            offline_count = 0
            
            for d_id, data_str in all_drivers.items():
                payload = json.loads(data_str)
                status = payload.get("status", "OFFLINE")
                
                if status == "AVAILABLE":
                    available_count += 1
                elif status == "ON_TRIP":
                    ontrip_count += 1
                else:
                    offline_count += 1
                    
                parsed_drivers.append({
                    "Driver ID": d_id,
                    "latitude": float(payload.get("latitude", 0.0)),
                    "longitude": float(payload.get("longitude", 0.0)),
                    "Operational Status": status,
                    "Last Transmission (UTC)": payload.get("last_updated", "")
                })
            
            # Map array to a structured DataFrame
            df = pd.DataFrame(parsed_drivers)
            
            # 5. Core Metric Card Layout
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            metric_col1.metric("Total Monitored Fleet", f"{len(df)} Cars")
            metric_col2.metric("🟢 Available Status", f"{available_count} Cars")
            metric_col3.metric("🟡 Active Trip Status", f"{ontrip_count} Cars")
            metric_col4.metric("🔴 Offline Status", f"{offline_count} Cars")
            
            st.markdown("---")
            
            # 6. Interactive Geospatial Mapping Layer
            st.subheader("🗺️ Live Fleet Geospatial Map Projection")
            # Streamlit maps require explicit lower-case 'latitude' and 'longitude' labels
            st.map(df, size=40, color="#1f77b4" if available_count > 0 else "#ff7f0e")
            
            st.markdown("---")
            
            # 7. Complete Tabular Data Grid Overview
            st.subheader("📋 Core RAM Cache Table Registry")
            st.dataframe(
                df.sort_values(by="Driver ID"),
                use_container_width=True,
                hide_index=True
            )
            
            # Timestamp stamp reflecting last grid evaluation run
            st.caption(f"Last UI Render Scan: {datetime.now().strftime('%H:%M:%S')} | Target Broker Node: {REDIS_HOST}:{REDIS_PORT}")
            
    # Break out of the loop instantly if user unchecks 'Live Engine Tracking'
    if not auto_refresh:
        break
        
    time.sleep(refresh_interval)