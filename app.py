from flask import Flask, render_template, jsonify
import threading
import time
import os
from snmp_capture import capture_once

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# --- CONFIGURATION ---
POLL_INTERVAL = 5  # Seconds between starting a new scan
# ---------------------

def background_snmp_loop():
    """Continuous background polling."""
    print(f"[*] SNMP Background Thread Started. Interval: {POLL_INTERVAL}s")
    while True:
        try:
            start_time = time.time()
            capture_once()
            
            # Calculate how long the scan took to keep the interval steady
            elapsed = time.time() - start_time
            sleep_time = max(0, POLL_INTERVAL - elapsed)
            
            time.sleep(sleep_time)
        except Exception as e:
            print(f"[!] Loop Error: {e}")
            time.sleep(10)

@app.route("/")
def index():
    return "SNMP Monitor is Running. View the Streamlit dashboard for status."

if __name__ == "__main__":
    # 1. Start the background thread
    # use_reloader=False is CRITICAL to prevent double-polling
    t = threading.Thread(target=background_snmp_loop, daemon=True)
    t.start()
    
    # 2. Start Flask (Port 5005 as requested)
    # Turning off the reloader keeps the background thread from doubling up
    print("[*] Starting Web Server on http://0.0.0.0:5005")
    app.run(host="0.0.0.0", port=5005, debug=True, use_reloader=False)