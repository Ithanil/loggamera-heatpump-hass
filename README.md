# Loggamera Heat Pump Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?logo=HomeAssistantCommunityStore&logoColor=white)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A custom Home Assistant integration for reading heat pump snapshot data from the
[Loggamera](https://loggamera.se/) API.

## Features

- Fetches the latest heat pump snapshot every 15 minutes.
- Creates temperature sensors for indoor, outdoor, hot water, heat carrier,
  brine, and pool values when the device exposes them.
- Creates status sensors for pump type, activity, fan state, alarm text, and
  last Loggamera timestamp.
- Creates binary sensors for active alarms, filter alarms, hot water extra, and
  reduced mode when supported by the device.
- Uses the Loggamera capabilities endpoint to avoid creating unsupported
  entities where the API reports capabilities.

## Requirements

- A heat pump, cooling device, or ventilation device connected to Loggamera.
- An active Loggamera account.
- Loggamera API access, API key, and device ID.

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Go to Integrations and add a custom repository for this repository.
3. Install **Loggamera Heat Pump**.
4. Restart Home Assistant.

### Manual

1. Copy `custom_components/loggamera_heatpump/` into
   `config/custom_components/loggamera_heatpump/`.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**.
4. Search for **Loggamera Heat Pump** and follow the setup flow.

## Configuration

The setup flow asks for:

- API Key
- Device ID
- Name, optional and defaulting to `Loggamera Heat Pump`

The integration validates the credentials by fetching a heat pump snapshot
during setup.

## API Usage

This integration uses the HeatPump part of the Loggamera Public API:

https://documenter.getpostman.com/view/6665372/S11HtyXG

The main endpoint is `POST https://platform.loggamera.se/Api/v1/HeatPump`.
The integration omits `DateTimeUtc` so Loggamera returns the freshest available
data. It also calls `POST https://platform.loggamera.se/Api/v1/GetCapabilities`
to discover supported fields.

## Entities

Entity availability depends on the values and capabilities returned by your
Loggamera device.

| Entity | Type | Notes |
| --- | --- | --- |
| Indoor temperature | Sensor | Celsius |
| Target indoor temperature | Sensor | Celsius |
| Hot water temperature | Sensor | Celsius |
| Outdoor temperature | Sensor | Celsius |
| Pool temperature | Sensor | Celsius |
| Heat carrier in/out | Sensor | Celsius |
| Brine in/out | Sensor | Celsius |
| Last log time | Sensor | Timestamp from Loggamera |
| Pump type | Sensor | For example `NibeF` |
| Activity | Sensor | For example `HEATING` |
| Alarm text | Sensor | Clear-text alarm information |
| Holiday reduction days | Sensor | Days |
| Fan state | Sensor | Reported fan setting |
| Alarm | Binary sensor | Problem device class |
| Filter alarm | Binary sensor | Problem device class |
| Hot water extra | Binary sensor | Enabled or disabled |
| Reduced mode | Binary sensor | Enabled or disabled |

## Development

This integration uses Home Assistant's async APIs and a `DataUpdateCoordinator`
so all entities share one polling cycle.

To test in a Home Assistant development environment:

```bash
hass -c /path/to/config
```

## Credits

This repository was derived from Svante Jacobsen's Loggamera power meter
integration:

https://github.com/svante-jacobsen/loggamera-home-assistant

The original project is licensed under the MIT License.
