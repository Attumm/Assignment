from .models import Quote

raw_quotes = [{
    "author": "Shakti Gawain",
    "text": "The more light you allow within you, the brighter the world you live in will be.",
    "tags": [
        "Famous Quotes"
    ],
    "source": "fallback"
}, {
    "author": "Richard Bach",
    "text": "In order to live free and happily you must sacrifice boredom. It is not always an easy sacrifice.",
    "tags": [
        "Famous Quotes"
    ],
    "source": "fallback"
}, {
    "author": "Napoleon Hill",
    "text": "Ideas are the beginning points of all fortunes.",
    "tags": [
        "Famous Quotes"
    ],
    "source": "quotable"
}
]

fall_back_quotes = [Quote(**item) for item in raw_quotes]  # type: ignore
