"""Support for MikroTik Netwatch sensors."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MikroTik Netwatch sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    if coordinator.data:
        for netwatch_item in coordinator.data:
            entities.append(
                MikroTikNetwatchSensor(
                    coordinator=coordinator,
                    netwatch_item=netwatch_item,
                    config_entry=config_entry,
                )
            )

    async_add_entities(entities)


class MikroTikNetwatchSensor(CoordinatorEntity, SensorEntity):
    """Representation of a MikroTik Netwatch sensor."""

    def __init__(
        self,
        coordinator,
        netwatch_item: dict[str, Any],
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._netwatch_item = netwatch_item
        self._config_entry = config_entry

        # Use the .id field for unique identification
        self._netwatch_id = netwatch_item.get(".id", "unknown")

        # Generate unique_id and entity_id
        host = config_entry.data["host"]
        self._attr_unique_id = f"{host}_{self._netwatch_id}_netwatch"

        # Use name if available, otherwise use host for name
        name = netwatch_item.get("name", netwatch_item.get("host", "unknown"))
        self._attr_name = f"Netwatch {name}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor (up/down status)."""
        if self.coordinator.data:
            # Find our specific netwatch item in the current data
            for item in self.coordinator.data:
                if item.get(".id") == self._netwatch_id:
                    return item.get("status")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self.coordinator.data:
            # Find our specific netwatch item in the current data
            for item in self.coordinator.data:
                if item.get(".id") == self._netwatch_id:
                    # Return all attributes except the ones we don't want to expose
                    attributes = item.copy()
                    # Remove the status since it's the main sensor value
                    attributes.pop("status", None)
                    return attributes
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        host = self._config_entry.data["host"]
        return {
            "identifiers": {(DOMAIN, host)},
            "name": f"MikroTik RouterOS ({host})",
            "manufacturer": "MikroTik",
            "model": "RouterOS",
        }
