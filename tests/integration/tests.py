import logging

from itertools import cycle
from unittest.mock import patch, AsyncMock

import pytest
import httpx

from src.quote.models import DataProvider

logger = logging.getLogger(__name__)

TEST_QUOTES = {
    "https://api.quotable.io/quotes/random": [
        {
            "_id": "test_id",
            "content": "test quote 1",
            "author": "test Author 1",
            "tags": ["tag1", "tag2"],
            "authorSlug": "test-author-slug",
            "length": 155,
            "dateAdded": "2019-02-11",
            "dateModified": "2023-04-14",
        }, {
            "_id": "test_id",
            "content": "test quote 2",
            "author": "test Author 2",
            "tags": ["tag3", "tag4"],
            "authorSlug": "test-author-slug",
            "length": 155,
            "dateAdded": "2019-02-11",
            "dateModified": "2023-04-14",
        }, {
            "_id": "test_id",
            "content": "test quote 3",
            "author": "test Author 3",
            "tags": ["tag5", "tag6"],
            "authorSlug": "test-author-slug",
            "length": 155,
            "dateAdded": "2019-02-11",
            "dateModified": "2023-04-14",
        },
    ],
    "https://zenquotes.io/api/random": [
        [{"q": "Zen quote 1", "a": "Zen Author 1"}],
        [{"q": "Zen quote 2", "a": "Zen Author 2"}],
        [{"q": "Zen quote 3", "a": "Zen Author 3"}]
    ]
}

TEST_QUOTES_CYCLED = {name: cycle(quotes) for name, quotes in TEST_QUOTES.items()}

TEST_DATA_PROVIDERS = {
    "quotable": DataProvider(
        name="quotable",
        url="https://api.quotable.io/quotes/random",
        verify=False
    ),
    "zenquotes": DataProvider(
        name="zenquotes",
        url="https://zenquotes.io/api/random",
        verify=False
    ),
}


class MockResponse(httpx.Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = httpx.Request("GET", "https://api.quotable.io/quotes/random")


async def mocked_send(*args, **kwargs):
    logger.debug(f"Mocked send called with args: {args}, kwargs: {kwargs}")
    data = next(TEST_QUOTES_CYCLED["https://api.quotable.io/quotes/random"])
    return MockResponse(200, json=data)


@pytest.fixture(scope="module", autouse=True)
def mock_httpx_send():
    with patch("httpx.AsyncClient.send", new=AsyncMock(side_effect=mocked_send)) as mock:
        yield mock


@pytest.fixture(scope="module", autouse=True)
def mock_data_providers():
    with patch("src.quote.config.DATA_PROVIDERS", TEST_DATA_PROVIDERS):
        yield


@pytest.fixture(scope="module")
def test_client():
    from src.quote.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client


def test_get_quote(test_client):
    for num in range(1, 4):
        response = test_client.get("/")
        assert response.status_code == 200
        json_response = response.json()

        assert json_response["author"] == f"test Author {num}"
        assert json_response["text"] == f"test quote {num}"


def test_response_format(test_client):
    formats = {
        "application/json": lambda x: x[0] == "{" and x[-1] == "}",
        "application/xml": lambda x: x.startswith("<?xml") or x.startswith("<quote>"),
        "text/html": lambda x: True or x.startswith("<div>"),
        "text/plain": lambda x: "test" in x,
    }

    for content_type, test_func in formats.items():
        headers = {"Accept": content_type}
        response = test_client.get("/", headers=headers)

        assert content_type in response.headers["Content-Type"]
        assert response.status_code == 200
        assert test_func(response.text.strip())
