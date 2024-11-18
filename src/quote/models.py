from typing import Any

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Quote:
    """Internal representation of a quote."""

    author: str
    text: str
    tags: tuple[str, ...]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'author': self.author,
            'text': self.text,
            'tags': list(self.tags),
            "source": self.source,
        }


@dataclass
class DataProvider:
    """The config about DataProvider."""

    name: str
    url: str
    verify: bool = True
    timeout: int = 10
