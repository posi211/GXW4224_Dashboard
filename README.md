# GXW4224 Dashboard

<img width="1149" height="489" alt="image" src="https://github.com/user-attachments/assets/f11b091f-89ae-4a50-836a-7d1c5e3157eb" />


A lightweight Python dashboard for monitoring a Grandstream GXW4224(v2) FXS gateway over SNMP — shows which ports are registered and active (on-hook, ringing, in-call) in near real time (~5–10s delay).

## How it works

- `snmp_capture.py` polls the gateway via SNMP and writes results to `snmp_log.json`
- `app.py` runs the polling loop in the background and serves a small Flask app
- `dashboard.py` is the Streamlit front end that reads the log and displays port status
- `start_snmp.bat` launches both on Windows

## Setup

### 1. Configure the gateway

Log in to the GXW4224's web admin and enable SNMP:

1. Enable SNMP: **Yes**
2. SNMP Version: **Version 2c**
3. SNMP Port: **10161** (avoids conflicting with anything using the default 161)
4. SNMPv1/v2c Community: *(choose your own community string — treat this like a password)*

### 2. Configure the dashboard

Copy the example config and fill in your own values:

\`\`\`bash
cp devices.yaml.example devices.yaml
\`\`\`

Edit `devices.yaml`:

- `host` — your gateway's IP address
- `port` — `10161` (or whatever you set above)
- `community` — the community string you set above

`devices.yaml` is gitignored, so your real values stay local.

### 3. Install dependencies

\`\`\`bash
pip install flask pysnmp pyyaml streamlit
\`\`\`

### 4. Run

\`\`\`bash
start_snmp.bat
\`\`\`

or manually:

\`\`\`bash
python app.py
streamlit run dashboard.py
\`\`\`

## Security notes

- Your SNMP community string acts like a password — never commit `devices.yaml` with real values.
- `app.py` runs Flask with `debug=True` for development convenience. If you expose this beyond localhost, set `debug=False` — the Werkzeug debugger allows remote code execution if reachable.
- Logs (`snmp_log.json`, `app_log.txt`) are gitignored since they're regenerated locally and may contain your real IP.

## Quick install (Windows)

1. Download [`setup.ps1`](setup.ps1)
2. Right-click it → **Run with PowerShell**

That's it — it installs Python if needed, downloads this project, installs dependencies, walks you through `devices.yaml`, and launches the dashboard.

If Windows blocks the script with an execution-policy error, open PowerShell and run:
\`\`\`powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
\`\`\`

Prefer to do it by hand, or on macOS/Linux? See [Manual setup](#manual-setup) below.
