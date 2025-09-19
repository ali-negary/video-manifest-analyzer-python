from abc import ABC, abstractmethod
from typing import Any


class IParser(ABC):
    @abstractmethod
    def analyze(self, manifest: str) -> Any:
        """Analyze a manifest string and return structured result."""
        pass
