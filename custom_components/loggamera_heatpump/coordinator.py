from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LoggameraHeatPumpApi, LoggameraHeatPumpApiError
from .const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_NAME,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoggameraHeatPumpData:
    snapshot: dict[str, Any]
    read_capabilities: tuple[str, ...]
    write_capabilities: tuple[str, ...]


class LoggameraHeatPumpCoordinator(DataUpdateCoordinator[LoggameraHeatPumpData]):
    """Fetches and stores Loggamera heatpump data for all platforms."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.api_key: str = entry.data[CONF_API_KEY]
        self.device_id: int = entry.data[CONF_DEVICE_ID]
        self.device_name: str = entry.data.get(CONF_NAME, DEFAULT_NAME)
        self.api = LoggameraHeatPumpApi(
            async_get_clientsession(hass), self.api_key, self.device_id
        )
        self._read_capabilities: tuple[str, ...] = ()
        self._write_capabilities: tuple[str, ...] = ()
        self._capabilities_loaded = False

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> LoggameraHeatPumpData:
        try:
            snapshot = await self.api.async_get_snapshot()
            await self._async_load_capabilities()
        except LoggameraHeatPumpApiError as err:
            raise UpdateFailed(
                f"Failed to fetch Loggamera heatpump data: {err}"
            ) from err

        return LoggameraHeatPumpData(
            snapshot=snapshot,
            read_capabilities=self._read_capabilities,
            write_capabilities=self._write_capabilities,
        )

    async def _async_load_capabilities(self) -> None:
        if self._capabilities_loaded:
            return

        capabilities = await self.api.async_get_capabilities()
        self._read_capabilities = tuple(capabilities.get("ReadCapabilities") or ())
        self._write_capabilities = tuple(capabilities.get("WriteCapabilities") or ())
        self._capabilities_loaded = True
