import time
import psutil
import datetime

uptime_seconds = time.time() - psutil.boot_time()
uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))

print(uptime_str)
