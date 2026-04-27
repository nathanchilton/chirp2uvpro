from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Channel

class BaseParser(ABC):
    """
    Base class for all parsers.
    Converts input format (string, file content, etc.) to a list of Channel objects.
    """
    @abstractmethod
    def parse(self, content: str) -> List[Channel]:
        """
        Parses the input content and returns a list of Channel objects.
        """
        pass

class BaseGenerator(ABC):
    """
    Base class for all generators.
    Converts a list of Channel objects to a specific output format (string).
    """
    @abstractmethod
    def generate(self, channels: List[Channel]) -> str:
        """
        Generates the output string from the list of Channel objects.
        """
        pass
