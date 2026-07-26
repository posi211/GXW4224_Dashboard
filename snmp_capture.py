import json
import yaml
import time
import os
from datetime import datetime
from pysnmp.hlapi import *

# Resolve all file paths relative to THIS script's location, not the
# process's current working directory. This is what makes the script
# work no matter how/where it's launched from (batch file, shortcut,
# different install path on new hardware, etc).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "snmp_log.json")
DEVICES_FILE = os.path.join(BASE_DIR, "devices.yaml")

# How many OIDs to bundle into a single SNMP GET request. SNMP supports
# many varbinds per PDU, so batching turns dozens of round trips into a
# handful. Kept conservative to avoid oversized UDP packets on
# low-end devices like the GXW.
BATCH_SIZE = 12


def load_devices():
    """Loads configuration from devices.yaml."""
    if not os.path.exists(DEVICES_FILE):
        print(f"[!] devices.yaml not found at {DEVICES_FILE}")
        return []
    with open(DEVICES_FILE, "r") as f:
        config = yaml.safe_load(f)
        return config.get("devices", [])


def _chunk(items, size):
    items = list(items)
    for i in range(0, len(items), size):
        yield items[i:i + size]


def snmp_get_batch(host, port, community, oid_map):
    """SNMP GET for multiple OIDs in as few round trips as possible.
    oid_map: {label: oid}. Returns {label: value_string}.

    IMPORTANT: creates its own SnmpEngine, scoped to this single call.
    pysnmp's engine is tied to asyncio, and asyncio event loops are
    thread-local - app.py runs this from a background thread, so a
    shared/global engine created elsewhere (e.g. at import time in the
    main thread) breaks silently and every OID comes back "None".
    Creating the engine here keeps it in the thread that actually uses
    it, while still batching OIDs per request for speed.
    """
    engine = SnmpEngine()
    results = {}

    for chunk in _chunk(oid_map.items(), BATCH_SIZE):
        labels = [label for label, _ in chunk]
        object_types = [ObjectType(ObjectIdentity(oid)) for _, oid in chunk]

        try:
            iterator = getCmd(
                engine,
                CommunityData(community),
                UdpTransportTarget((host, port), timeout=1.5, retries=1),
                ContextData(),
                *object_types
            )
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

            if errorIndication:
                print(f"[SNMP ERROR] {host}: {errorIndication}")
                for label in labels:
                    results[label] = "None"
                continue
            if errorStatus:
                print(f"[SNMP ERROR] {host}: {errorStatus.prettyPrint()} at {errorIndex}")
                for label in labels:
                    results[label] = "None"
                continue

            for label, varBind in zip(labels, varBinds):
                val = str(varBind[1].prettyPrint())
                results[label] = "N/A" if "No Such" in val else val

        except Exception as e:
            print(f"[SNMP EXCEPTION] {host}: {repr(e)}")
            for label in labels:
                results[label] = "None"

    return results


def capture_once():
    """Polls all devices and saves results to the log."""
    devices = load_devices()
    entries = []

    if not devices:
        print("[!] No devices loaded - check devices.yaml path/content.")
        return entries

    for dev in devices:
        print(f"[*] Polling {dev['name']}...")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "device": dev["name"],
            "host": dev["host"],
            "data": {}
        }

        entry["data"] = snmp_get_batch(
            dev["host"],
            dev.get("port", 161),
            dev["community"],
            dev["oids"]
        )

        entries.append(entry)

    append_log(entries)
    return entries


def append_log(entries):
    """Saves data to JSON and manages file size."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                log = json.load(f)
        else:
            log = []
    except json.JSONDecodeError:
        log = []

    log.extend(entries)
    # Keep only the last 2000 entries for better dashboard performance
    log = log[-2000:]

    # Atomic write: write to a temp file first, then swap it into place.
    # os.replace() is atomic on both Windows and Linux, so a reader
    # (e.g. dashboard.py polling every 2s) always sees either the
    # complete old file or the complete new one - never a truncated
    # or half-written file mid-swap.
    tmp_file = LOG_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(log, f, indent=2)
    os.replace(tmp_file, LOG_FILE)


if __name__ == "__main__":
    # Quick standalone test: run this file directly to confirm paths
    # resolve correctly and see any SNMP errors, regardless of cwd.
    print(f"[*] BASE_DIR: {BASE_DIR}")
    print(f"[*] DEVICES_FILE: {DEVICES_FILE}")
    print(f"[*] LOG_FILE: {LOG_FILE}")
    result = capture_once()
    print(json.dumps(result, indent=2))
