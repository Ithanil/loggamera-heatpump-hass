from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LoggameraHeatPumpCoordinator


@dataclass(frozen=True, kw_only=True)
class LoggameraHeatPumpBinarySensorDescription(BinarySensorEntityDescription):
    value_keys: tuple[str, ...]


BINARY_SENSORS: tuple[LoggameraHeatPumpBinarySensorDescription, ...] = (
    LoggameraHeatPumpBinarySensorDescription(
        key="alarm_active",
        name="Alarm",
        value_keys=("AlarmActive",),
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    LoggameraHeatPumpBinarySensorDescription(
        key="filter_alarm_active",
        name="Filter alarm",
        value_keys=("FilterAlarmActive",),
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    LoggameraHeatPumpBinarySensorDescription(
        key="hot_water_extra_enabled",
        name="Hot water extra",
        value_keys=("HotWaterExtraEnabled", "SetHotWaterExtraEnabled"),
    ),
    LoggameraHeatPumpBinarySensorDescription(
        key="reduced_mode_enabled",
        name="Reduced mode",
        value_keys=("SetReducedModeEnabled",),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: LoggameraHeatPumpCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LoggameraHeatPumpBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
        if _description_supported(coordinator, description.value_keys)
    )


class LoggameraHeatPumpBinarySensor(
    CoordinatorEntity[LoggameraHeatPumpCoordinator], BinarySensorEntity
):
    entity_description: LoggameraHeatPumpBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LoggameraHeatPumpCoordinator,
        description: LoggameraHeatPumpBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{coordinator.device_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        pump_type = _first_value(self.coordinator.data.snapshot, ("PumpType",))
        device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self.coordinator.device_id))},
            manufacturer="Loggamera",
            name=self.coordinator.device_name,
        )
        if pump_type:
            device_info["model"] = str(pump_type)
        return device_info

    @property
    def is_on(self) -> bool | None:
        value = _first_value(
            self.coordinator.data.snapshot,
            self.entity_description.value_keys,
        )
        if value is None:
            return None

        return bool(value)


def _description_supported(
    coordinator: LoggameraHeatPumpCoordinator, value_keys: tuple[str, ...]
) -> bool:
    snapshot = coordinator.data.snapshot
    capabilities = set(coordinator.data.read_capabilities)
    return any(
        key in snapshot and snapshot[key] not in (None, "") for key in value_keys
    ) or any(
        key in capabilities for key in value_keys
    )


def _first_value(snapshot: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in snapshot:
            return snapshot[key]
    return None
