"""
Model of asyncio.run_in_threadpool  ThreadPool.
"""

import asyncio
from collections.abc import Callable
from functools import partial
from typing import TypeVar

from typing_extensions import ParamSpec


R = TypeVar("R")
P = ParamSpec("P")


async def run_in_threadpool(fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    kwargs_fn = partial(fn, *args, **kwargs)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, kwargs_fn)
