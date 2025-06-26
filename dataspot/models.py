"""Data models for dataspot patterns and structures."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Pattern:
    """A concentration pattern found in the data."""

    path: str
    count: int
    percentage: float
    depth: int
    samples: List[Dict[str, Any]]

    def __post_init__(self):
        """Post-initialization hook."""
        if self.samples is None:
            self.samples = []
