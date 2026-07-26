import time
from snmp_capture import capture_once

start = time.time()
capture_once()
print(f"Poll took {time.time() - start:.2f}s")