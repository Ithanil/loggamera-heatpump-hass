from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import aiohttp

from .const import (
    API_CAPABILITIES_URL,
    API_HEATPUMP_URL,
    API_TIMEOUT,
    CONF_API_KEY,
    CONF_DEVICE_ID,
)


class LoggameraHeatPumpApiError(Exception):
    """Base exception for Loggamera heatpump API errors."""


class LoggameraHeatPumpConnectionError(LoggameraHeatPumpApiError):
    """Raised when Home Assistant cannot reach the Loggamera API."""


class LoggameraHeatPumpApi:
    """Small async client for the Loggamera heatpump API."""

    def __init__(
        self, session: aiohttp.ClientSession, api_key: str, device_id: int
    ) -> None:
        self._session = session
        self._api_key = api_key
        self._device_id = device_id

    async def async_get_snapshot(
        self, date_time_utc: datetime | None = None
    ) -> dict[str, Any]:
        payload = self._base_payload()

        if date_time_utc is not None:
            payload["DateTimeUtc"] = _format_utc(date_time_utc)

        return await self._async_post(API_HEATPUMP_URL, payload)

    async def async_get_capabilities(self) -> dict[str, Any]:
        return await self._async_post(API_CAPABILITIES_URL, self._base_payload())

    def _base_payload(self) -> dict[str, Any]:
        return {
            "ApiKey": self._api_key,
            "DeviceId": self._device_id,
        }

    async def _async_post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with self._session.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as response:
                if response.status != 200:
                    raise LoggameraHeatPumpApiError(
                        f"Loggamera API returned HTTP {response.status}"
                    )

                data = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise LoggameraHeatPumpConnectionError(
                f"Could not connect to Loggamera API: {err}"
            ) from err
        except ValueError as err:
            raise LoggameraHeatPumpApiError(
                "Loggamera API returned invalid JSON"
            ) from err

        if not isinstance(data, dict):
            raise LoggameraHeatPumpApiError("Loggamera API returned invalid data")

        error = data.get("Error")
        if error:
            raise LoggameraHeatPumpApiError(str(error))

        result = data.get("Data")
        if not isinstance(result, dict):
            raise LoggameraHeatPumpApiError("Loggamera API response is missing Data")

        return result


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
