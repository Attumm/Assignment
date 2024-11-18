from typing import Any

from .models import Quote


def provider_quotable_parsing(data: dict[str, Any]) -> Quote:
    """
    Parse data from quotable service into a Quote object.

    Args:
        data (dict): Raw data from Quotable data provider service.

    Returns:
        Quote: Parsed Quote object.

    Example:
        {
            "_id": "Bjvcw8bqPmEJ",
            "content": "Her it.",
            "author": "Napoleon Hill",
            "tags": ["Success"],
            "authorSlug": "napoleon-hill",
            "length": 155,
            "dateAdded": "2019-02-11",
            "dateModified": "2023-04-14"
        }
    """
    return Quote(
        author=data["author"],
        text=data["content"],
        tags=tuple(data["tags"]),
        source="quotable"
    )


def provider_zenquotes_parsing(data: dict[str, Any]) -> Quote:
    """
    Parse data from Zenquotes service into a Quote object.

    Args:
        data (dict): Raw data from Zenquotes data provider service.

    Returns:
        Quote: Parsed Quote object.

    Example:
        {
            "q": "Thinking is difficult, that's why most people judge.",
            "a": "Carl Jung",
            "h": "<blockquote>&lg</footer></blockquote>"
        }
    """
    return Quote(
        author=data["a"],
        text=data["q"],
        tags=tuple(),
        source="zenquotes"
    )


PARSERS = {
    "quotable": provider_quotable_parsing,
    "zenquotes": provider_zenquotes_parsing,
}


def create_quote(name_provider: str, data: dict[str, Any]) -> Quote:
    """
    Parse quote data from a specified service into a Quote object.

    Uses a branch table (PARSERS dict) to select the appropriate parsing function.

    Args:
        name_provider (str): Name of the quote provider (e.g., "quotable", "zenquotes").
        data (dict[str, Any]): Raw quote data from the service.

    Returns:
        Quote: Parsed Quote object.

    Raises:
        NotImplementedError: If the specified service is not yet supported.
    """
    try:
        parser = PARSERS[name_provider]
    except KeyError:
        raise NotImplementedError(
            f"Unknown service: {name_provider}, not implemented yet known parsers: \
            {PARSERS.keys()}")

    return parser(data)
