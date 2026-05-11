import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_AUTODARTS_PORT, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_AUTODARTS_PORT

class DartsHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=f"Darts Hub ({user_input[CONF_HOST]})", 
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Required(CONF_AUTODARTS_PORT, default=DEFAULT_AUTODARTS_PORT): int,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)