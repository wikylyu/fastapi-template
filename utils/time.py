import time


def get_short_time(t: float) -> str:
    local_time = time.localtime(t)
    return time.strftime("%y/%m/%d %H:%M:%S", local_time)
