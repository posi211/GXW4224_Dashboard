import streamlit as st
import json
import os

st.set_page_config(page_title="NOC Port Monitor", layout="wide")

# Uniform Box CSS - Added a slight background for better visibility
st.markdown("""
    <style>
    [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 140px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 10px !important;
        background-color: #f9f9f9;
    }
    .port-header { font-size: 1.1rem; font-weight: bold; color: #333; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Real-Time Port Monitor")

# Resolve the log file relative to this script's own location, not
# whatever directory Streamlit happened to be launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "snmp_log.json")

def get_latest_status():
    if not os.path.exists(LOG_FILE):
        return None
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)

        # Search from the end for the most recent Grandstream entry
        for entry in reversed(data):
            if entry.get("device") == "Grandstream-GXW4224v2":
                return entry
        return None
    except:
        return None

# Fragment refreshes every 2 seconds to match your polling speed
@st.fragment(run_every=2)
def show_port_grid():
    latest_entry = get_latest_status()

    if latest_entry:
        ts = latest_entry.get("timestamp", "N/A")
        # Clean up timestamp for display
        display_time = ts.split('T')[-1].split('.')[0]
        data = latest_entry.get("data", {})

        st.caption(f"Last Device Sync: {display_time}")
        cols = st.columns(6)

        for i in range(1, 25):
            col_idx = (i - 1) % 6
            with cols[col_idx]:
                # Keys match the portX_reg format in devices.yaml
                reg = str(data.get(f"port{i}_reg", "None")).strip()
                hook = str(data.get(f"port{i}_hook", "None")).strip()

                with st.container(border=True):
                    st.markdown(f"<div class='port-header'>Port {i}</div>", unsafe_allow_html=True)

                    if reg == "0":
                        if hook == "2": st.warning("RINGING 🔔")
                        elif hook == "5": st.success("IN CALL 📞")
                        elif hook == "4": st.warning("OFF HOOK ⚠️")
                        else: st.info("ACTIVE ✅")
                    elif reg == "1":
                        st.error("UNREG ❌")
                    else:
                        st.write("OFFLINE ⚪")
    else:
        st.warning("No data found in snmp_log.json. Check if app.py is running.")

# Start the fragment
show_port_grid()
