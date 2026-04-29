from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LoggameraHeatPumpCoordinator


@dataclass(frozen=True, kw_only=True)
class LoggameraHeatPumpSensorDescription(SensorEntityDescription):
    value_keys: tuple[str, ...]
    value_fn: Callable[[Any], Any] = lambda value: value


def _as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


TEMPERATURE_SENSORS: tuple[LoggameraHeatPumpSensorDescription, ...] = (
    LoggameraHeatPumpSensorDescription(
        key="indoor_temperature",
        name="Indoor temperature",
        value_keys=("IndoorTemperature",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="target_indoor_temperature",
        name="Target indoor temperature",
        value_keys=("SetIndoorTemp",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="hot_water_temperature",
        name="Hot water temperature",
        value_keys=("HotWaterTemp", "HotwaterTemp"),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="outdoor_temperature",
        name="Outdoor temperature",
        value_keys=("OutdoorTemp",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="pool_temperature",
        name="Pool temperature",
        value_keys=("PoolTemp",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="heat_carrier_in",
        name="Heat carrier in",
        value_keys=("HeatCarrierIn",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="heat_carrier_out",
        name="Heat carrier out",
        value_keys=("HeatCarrierOut",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="brine_in",
        name="Brine in",
        value_keys=("BrineIn",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="brine_out",
        name="Brine out",
        value_keys=("BrineOut",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
)

OTHER_SENSORS: tuple[LoggameraHeatPumpSensorDescription, ...] = (
    LoggameraHeatPumpSensorDescription(
        key="last_log_time",
        name="Last log time",
        value_keys=("LogDateTimeUtc",),
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_as_datetime,
    ),
    LoggameraHeatPumpSensorDescription(
        key="pump_type",
        name="Pump type",
        value_keys=("PumpType",),
    ),
    LoggameraHeatPumpSensorDescription(
        key="activity",
        name="Activity",
        value_keys=("Activity",),
    ),
    LoggameraHeatPumpSensorDescription(
        key="alarm_text",
        name="Alarm text",
        value_keys=("AlarmInClearText", "AlarmClearText"),
    ),
    LoggameraHeatPumpSensorDescription(
        key="holiday_reduction_days",
        name="Holiday reduction days",
        value_keys=("SetHolidayReductionDays",),
        native_unit_of_measurement="d",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_as_float,
    ),
    LoggameraHeatPumpSensorDescription(
        key="fan_state",
        name="Fan state",
        value_keys=("SetFanState",),
    ),
)

SENSORS = TEMPERATURE_SENSORS + OTHER_SENSORS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: LoggameraHeatPumpCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LoggameraHeatPumpSensor(coordinator, description)
        for description in SENSORS
        if _description_supported(coordinator, description.value_keys)
    )


class LoggameraHeatPumpSensor(
    CoordinatorEntity[LoggameraHeatPumpCoordinator], SensorEntity
):
    entity_description: LoggameraHeatPumpSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LoggameraHeatPumpCoordinator,
        description: LoggameraHeatPumpSensorDescription,
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
    def native_value(self) -> Any:
        value = _first_value(
            self.coordinator.data.snapshot,
            self.entity_description.value_keys,
        )
        return self.entity_description.value_fn(value)


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
