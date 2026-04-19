from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseParser(ABC):
    """
    Base class for all parsers.
    Converts input format (string, file content, etc.) to an internal list of channel dictionaries.
    """
    @abstractmethod
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parses the input content and returns a list of channel dictionaries.
        """
        pass

class BaseGenerator(ABC):
    """
    Base class for all generators.
    Converts an internal list of channel dictionaries to a specific output format (string).
    """
    @abstractmethod
    def generate(self, channels: List[Dict[str, Any]]) -> str:
        """
        Generates the output string from the list of channel dictionaries.
        """
        pass
