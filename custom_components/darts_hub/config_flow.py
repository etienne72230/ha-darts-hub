import voluptuous as vol
import aiohttp
import asyncio
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT

class CannotConnect(Exception):
    """Error to indicate we cannot connect."""

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    url = f"wss://{host}:{port}/socket.io/?transport=websocket&EIO=4"
    
    session = async_get_clientsession(hass)
    
    try:
        # Attempt a quick connection to verify server availability
        async with session.ws_connect(url, ssl=False, timeout=5) as ws:
            pass
    except (aiohttp.ClientError, asyncio.TimeoutError):
        raise CannotConnect

    return {"title": f"Darts Hub ({host})"}

class DartsHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Darts Hub."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                return self.async_create_entry(
                    title=info["title"], 
                    data=user_input
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )