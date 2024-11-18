from typing import Optional, Dict, Any

import logging

import httpx

from .models import DataProvider


logger = logging.getLogger(__name__)


async def fetch_data_from(data_provider: DataProvider) -> Optional[Dict[str, Any]]:
    logger.debug("Fetching data from: %s", data_provider.url)
    async with httpx.AsyncClient(verify=data_provider.verify, timeout=data_provider.timeout) as client:
        try:
            response = await client.get(data_provider.url)
            response.raise_for_status()
            data = response.json()
            logger.debug("Successfully fetched data from %s", data_provider.url)
            # Most services return one quote within a list, there is no time but to make
            # data handling per data_provider would be maintainable and flexible solution.
            # below is to pass mypy --strict
            if isinstance(data, dict):
                return data
            if isinstance(data, list) and data and isinstance(data[0], dict):
                return data[0]

            logger.error("Unexpected data format from %s",data_provider.url)
            return None

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error occurred while fetching data from %s: %s", data_provider.url, str(e))
        except Exception as e:
            logger.error("An error occurred while fetching data from %s: %s", data_provider.url, str(e))
    return None
