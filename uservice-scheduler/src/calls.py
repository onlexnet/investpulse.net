from asyncio import Queue
from datetime import datetime, timedelta
import logging
import time
from typing import Callable


def invocation_counter(func: Callable) -> Callable:

    def wrapper(*args, **kwargs):
    
        now = datetime.now().replace(microsecond=0)
        if wrapper.invocation_count == 0:
            wrapper.reported_first = now

        time_delta = now - wrapper.reported_when
        # report progress every 3 secs
        if time_delta >= timedelta(seconds=3):
            wrapper.reported_when = now
            total_delta: timedelta = now - wrapper.reported_first
            total_time_secs: float = total_delta.total_seconds()
            average_per_sec = '---'
            if total_time_secs > 0:
                average_per_sec = int(wrapper.invocation_count / total_time_secs)
            logging.info(f"time: {now}, total events: {wrapper.invocation_count}, average events / sec: {average_per_sec}")

        wrapper.invocation_count = wrapper.invocation_count + 1
    
        return func(*args, **kwargs)
    
    now = datetime.now()
    wrapper.reported_when = now
    wrapper.reported_first = now
    wrapper.invocation_count = 0
    return wrapper