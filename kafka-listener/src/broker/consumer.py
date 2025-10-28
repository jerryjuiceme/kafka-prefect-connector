from abc import ABC, abstractmethod
import asyncio
from email.message import EmailMessage
import logging
from typing import AsyncGenerator
import typing

from pydantic import ValidationError


from src.config import settings


logger = logging.getLogger(__name__)


class ConsumeBase(ABC):
    @abstractmethod
    async def process_message(self, msg: str):
        pass

class TriggerConsumer(ConsumeBase):
    
    async def process_message(self, msg: str):
        pass