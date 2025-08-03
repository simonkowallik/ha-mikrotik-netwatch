"""API client for MikroTik RouterOS Netwatch."""

from __future__ import annotations

import logging
import re
from typing import Any

import aiohttp
from aiohttp import BasicAuth

_LOGGER = logging.getLogger(__name__)

NETWATCH_TIME_KEYS = [
    "rtt-avg",
    "rtt-jitter",
    "rtt-max",
    "rtt-min",
    "rtt-stdev",
    "tcp-connect-time",
    "http-resp-time",
]


class MikroTikNetwatchAPI:
    """Minimal API client for MikroTik RouterOS Netwatch."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the API client."""
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = session
        self.base_url = f"https://{host}/rest/tool/netwatch"

    async def async_get_netwatch_data(self) -> list[dict[str, Any]]:
        """Get netwatch data from MikroTik RouterOS."""
        auth = BasicAuth(self.username, self.password)
        headers = {"Accept": "application/json"}

        try:
            async with self.session.get(
                self.base_url,
                auth=auth,
                headers=headers,
                ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return self._process_netwatch_data(data)

        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching netwatch data: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error fetching netwatch data: %s", err)
            raise

    def _process_netwatch_data(
        self, data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Process raw netwatch data to convert time values."""
        processed_data = []
        for item in data:
            processed_item = item.copy()

            # Convert time values from "11ms687us" format to milliseconds
            for key in NETWATCH_TIME_KEYS:
                if key in processed_item:
                    processed_item[key] = self._convert_time_to_ms(processed_item[key])

            processed_data.append(processed_item)
        return processed_data

    def _convert_time_to_ms(self, time_str: str) -> float | None:
        """Convert MikroTik time format (e.g., '11ms687us') to milliseconds."""
        if not time_str:
            return None

        try:
            # Pattern to match formats like "11ms687us", "11ms", "687us"
            pattern = r"(?:(\d+)ms)?(?:(\d+)us)?"
            match = re.match(pattern, time_str)

            if not match:
                return None

            ms_part = match.group(1)
            us_part = match.group(2)

            total_ms = 0.0

            if ms_part:
                total_ms += float(ms_part)

            if us_part:
                total_ms += (
                    float(us_part) / 1000.0
                )  # Convert microseconds to milliseconds

            return total_ms

        except (ValueError, AttributeError):
            _LOGGER.warning("Failed to convert time format: %s", time_str)
            return None
