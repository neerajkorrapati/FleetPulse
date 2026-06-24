import json
import os
import random
import time
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv
from kafka import KafkaProducer

# Load environment configuration from the root directory
load_dotenv(dotenv_path="../../.env")

KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL", "localhost:19092")
TOPIC_NAME = os.getenv("TELEMETRY_TOPIC", "driver-telemetry")

print(f"[BOOT] Initializing Telemetry Core connecting to Broker: {KAFKA_BROKER}")

# Initialize our Pure-Python Kafka Producer Gateway
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8")
)

# Base coordinates for the simulation grid (Centered around a city core)
BASE_LAT = 12.9716
BASE_LON = 77.5946

def simulate_single_driver(driver_id: str):
    """Generates continuous coordinate variations tracking a single vehicle path."""
    current_lat = BASE_LAT + random.uniform(-0.05, 0.05)
    current_lon = BASE_LON + random.uniform(-0.05, 0.05)
    
    statuses = ["AVAILABLE", "ON_TRIP", "OFFLINE"]
    current_status = random.choice(statuses)

    while True:
        # 1. Simulate minor vehicle movement
        current_lat += random.uniform(-0.0005, 0.0005)
        current_lon += random.uniform(-0.0005, 0.0005)
        
        # 5% chance to shift operational status dynamically
        if random.random() < 0.05:
            current_status = random.choice(statuses)

        # 2. Structure the standardized JSON Telemetry Payload Frame
        payload = {
            "driver_id": driver_id,
            "latitude": round(current_lat, 6),
            "longitude": round(current_lon, 6),
            "status": current_status,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # 3. Stream data utilizing the driver_id as the Partition Key
            producer.send(
                topic=TOPIC_NAME,
                key=driver_id,
                value=payload
            )
            print(f"[STREAMING] {driver_id} -> Lat: {payload['latitude']}, Lon: {payload['longitude']} | Status: {payload['status']}")
        except Exception as e:
            print(f"[ERROR] Failed transmission for {driver_id}: {str(e)}")

        # Wait between 1 to 3 seconds before broadcasting the next location ping
        time.sleep(random.uniform(1.0, 3.0))

if __name__ == "__main__":
    # Define how many active vehicles we want to scale out onto thread groups
    TOTAL_SIMULATED_DRIVERS = 10
    print(f"[LAUNCH] Deploying thread matrix for {TOTAL_SIMULATED_DRIVERS} parallel drivers...")

    threads = []
    for i in range(TOTAL_SIMULATED_DRIVERS):
        d_id = f"DRIVER_{i:03d}"
        t = Thread(target=simulate_single_driver, args=(d_id,), daemon=True)
        threads.append(t)
        t.start()

    # Keep the master coordinator script alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Terminating driver simulation matrix. Flushing queue buffers...")
        producer.flush()
        print("[SHUTDOWN] System offline.")