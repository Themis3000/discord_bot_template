"""Includes useful utilities for time based operations"""
from datetime import datetime, timezone
import time


def convert_millis_readable(millis: int):
    seconds = millis // 1000
    if seconds >= 3600:
        time_str = time.strftime("%H:%M:%S", time.gmtime(seconds))
    else:
        time_str = time.strftime("%M:%S", time.gmtime(seconds))
    if time_str.startswith("0"):
        return time_str[1:]
    return time_str


def get_current_milliseconds():
    dt = datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
    return dt.timestamp() / 1000
