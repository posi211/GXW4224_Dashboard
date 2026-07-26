# GXW4224_Dashboard
Grandstream GXW4224 Active Port Dashboard
this will show you if the port is registarted or active. Ringing, Inuse
There is a 5-10 second delay

To make this work we need to update the GXW4224.
login to the gateway and make the following changes
1. Enable SNMP = YES
2. SNMP Version = Version 2C
3. SNMP Port = 10161
4. SNMPv1/v2c Community = MyCommunityName

Update the devices.yaml
1.  host = Your device IP address
2.  port = 10161
3.  community name = MyCommunityNAme



