import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LoggameraHeatPumpApi, LoggameraHeatPumpApiError
from .const import CONF_API_KEY, CONF_DEVICE_ID, CONF_NAME, DEFAULT_NAME, DOMAIN


class LoggameraHeatPumpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            errors = {}
            try:
                await _validate_input(self.hass, user_input)
            except LoggameraHeatPumpApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{DOMAIN}_{user_input[CONF_DEVICE_ID]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )
        else:
            errors = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_DEVICE_ID): vol.Coerce(int),
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }),
            errors=errors,
        )


async def _validate_input(hass, user_input: dict) -> None:
    client = LoggameraHeatPumpApi(
        async_get_clientsession(hass),
        user_input[CONF_API_KEY],
        user_input[CONF_DEVICE_ID],
    )
    await client.async_get_snapshot()
