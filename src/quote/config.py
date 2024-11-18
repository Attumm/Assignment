import logging
from .models import DataProvider

DATA_PROVIDERS = {
    "quotable": DataProvider(
        name="quotable",
        url="https://api.quotable.io/quotes/random",
        verify=False
    ),
    "zenquotes":
        DataProvider(
            name="zenquotes",
            url="https://zenquotes.io/api/random"
    ),
}

DATA_PROVIDERS_CHOICES = tuple(DATA_PROVIDERS.items())
QUEUE_SIZE = 10
WORKER_PER_PROVIDER = 2
WORKER_SLEEP_AFTER_FAIL = 10

LOGGING_LEVEL = logging.INFO
