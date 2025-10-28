"""
Time utils module
"""

import datetime


def ts_now() -> float:
    """
    Returns current dattime timestamp UTC.

    :return: value in seconds
    """
    return datetime.datetime.now(datetime.UTC).timestamp()
