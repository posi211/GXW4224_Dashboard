from scapy.all import IP, UDP, SNMP, SNMPget, SNMPvarbind, sr1

host = "50.187.233.209"
community = "absitelecom"

# We will check Port 1, but also look for a "Table" index
test_oids = [
    "1.3.6.1.4.1.42397.1.1.2.1.0", # Port 1 (Alternative index)
    "1.3.6.1.4.1.42397.1.1.2.1.1", # Port 1 (Standard index)
    "1.3.6.1.4.1.42397.1.1.1.1.1", # A different branch in the MIB
]

for oid in test_oids:
    print(f"Scanning OID: {oid}")
    packet = IP(dst=host)/UDP(dport=10161)/SNMP(community=community, PDU=SNMPget(varbindlist=[SNMPvarbind(oid=oid)]))
    reply = sr1(packet, timeout=2, verbose=False)
    
    if reply and reply.haslayer(SNMP):
        val = reply[SNMP].PDU.varbindlist[0].value
        print(f"  -> Result: {val}")
    else:
        print("  -> Result: No Response")
