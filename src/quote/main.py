from typing import AsyncGenerator

import logging
import random
import asyncio

from contextlib import asynccontextmanager
from asyncio import Queue

from fastapi import FastAPI, Request, Response

from .models import Quote, DataProvider
from .parsing import create_quote
from .response_format import response_formatter, get_output_format
from .common import fetch_data_from

from .config import LOGGING_LEVEL, QUEUE_SIZE, DATA_PROVIDERS_CHOICES
from .config import DATA_PROVIDERS, WORKER_PER_PROVIDER, WORKER_SLEEP_AFTER_FAIL
from .static_data import fall_back_quotes

logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


data_queue: Queue[Quote] = Queue(maxsize=QUEUE_SIZE)


async def worker(worker_id: int, data_provider: DataProvider) -> None:
    """Fetches data from data_provider, adds it to a queue, and waits until there's room to repeat.

        This worker function runs in an infinite loop, performing the following steps:

        If fetching fails or an exception occurs, the worker backs off for a set time
        before retrying.

        Args:
            worker_id: An integer identifying the worker.
            data_provider: A DataProvider object
    """
    while True:
        logger.info("Worker %d started for %s", worker_id, data_provider.name)
        try:
            data = await fetch_data_from(data_provider)
            if data:
                quote = create_quote(data_provider.name, data)
                await data_queue.put(quote)
                logger.info(
                    "Worker %d Added data from %s to queue. Queue size: %d",
                    worker_id, data_provider.name, data_queue.qsize())
            else:
                logger.warning("Failed to fetch data from %s, sleep to backoff", data_provider.name)
                await asyncio.sleep(WORKER_SLEEP_AFTER_FAIL)
        except Exception as e:
            logger.exception(e)
            logger.warning("Exception occurred %s, sleep to backoff", data_provider.name)
            await asyncio.sleep(WORKER_SLEEP_AFTER_FAIL)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages the lifecycle of background tasks for data preloading.

    This function sets up background tasks to preload data from various providers
    at application startup and ensures proper shutdown of these tasks when the
    application is terminated. Scaffolding function.

    Args:
        _app: FastAPI application instance

    Yields:
        None: Control is yielded back to the FastAPI framework.
    """
    logger.info("Starting background task to preload data Queue size: %d", QUEUE_SIZE)
    logger.info("From the following data providers: %s.", ", ".join(DATA_PROVIDERS.keys()))
    tasks = []
    worker_id = 0
    for _ in range(WORKER_PER_PROVIDER):
        for data_provider in DATA_PROVIDERS.values():
            worker_id += 1
            tasks.append(
                asyncio.create_task(worker(worker_id, data_provider))
            )
    try:
        yield
    finally:
        logger.info("Shutting down, cancelling background tasks")
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                logger.debug("cancelled task")

app = FastAPI(lifespan=lifespan)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(content=b"", media_type="image/x-icon")


@app.get("/", responses={
    200: {
        "content": {
            "application/json": {},
            "application/xml": {},
            "text/html": {},
            "text/plain": {}
        },
    }
})
async def index(request: Request) -> Response:
    """
    Fastapi index API endpoint that returns a Quote.

    Returns a Quote from one of three sources:
    1. From a queue if available
    2. Directly from a randomly chosen data provider if queue is empty
    3. From fallback quotes if direct fetch fails

    The response format is determined based on the request's Accept header.

    Args:
        request: FastAPI Request instance.

    Returns:
        Response: Formatted Quote in JSON, XML, HTML, or plain text
    """
    if not data_queue.empty():
        quote = await data_queue.get()
        logger.info("Quote from queue. Queue size: %d", data_queue.qsize())
    else:
        logger.warning("Queue is empty, get data directly")
        _, data_provider = random.choice(DATA_PROVIDERS_CHOICES)  # nosec B311
        data = await fetch_data_from(data_provider)
        if data is not None:
            quote = create_quote(data_provider.name, data)
        else:
            quote = random.choice(fall_back_quotes)  # nosec B311
            logger.warning("Failed to directly fetch data from %s", data_provider.name)

    output_format = get_output_format(request)
    return response_formatter(quote, output_format)
