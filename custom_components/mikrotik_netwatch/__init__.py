"""The MikroTik Netwatch integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .api import MikroTikNetwatchAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup MikroTik Netwatch from a config entry."""

    api = MikroTikNetwatchAPI(
        host=entry.data["host"],
        username=entry.data["username"],
        password=entry.data["password"],
        verify_ssl=not entry.data.get("ignore_ssl", False),
        session=aiohttp_client.async_get_clientsession(hass),
    )

    coordinator = MikroTikNetwatchDataUpdateCoordinator(
        hass, api, entry.data.get("scan_interval", 10)
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class MikroTikNetwatchDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the MikroTik API."""

    def __init__(
        self, hass: HomeAssistant, api: MikroTikNetwatchAPI, scan_interval: int
    ) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.async_get_netwatch_data()
        except Exception as exception:
            raise UpdateFailed() from exception
