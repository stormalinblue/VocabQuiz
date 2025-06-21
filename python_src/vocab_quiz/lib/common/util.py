from datetime import datetime
import pytz

def utc_now_sec_timestamp() -> int:
    return int(datetime.now(pytz.utc).timestamp())