from homeassistant.const import Platform

DOMAIN = "loggamera_heatpump"

DEFAULT_NAME = "Loggamera Heat Pump"
DEFAULT_SCAN_INTERVAL = 900

CONF_API_KEY = "api_key"
CONF_DEVICE_ID = "device_id"
CONF_NAME = "name"

API_BASE_URL = "https://platform.loggamera.se/Api/v1"
API_HEATPUMP_URL = f"{API_BASE_URL}/HeatPump"
API_CAPABILITIES_URL = f"{API_BASE_URL}/GetCapabilities"
API_TIMEOUT = 10

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]
