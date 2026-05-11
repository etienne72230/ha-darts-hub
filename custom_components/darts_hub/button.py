from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

BUTTON_TYPES = [
    {"key": "board_reset", "name": "Reset Board", "icon": "mdi:restart", "endpoint": "reset"},
    {"key": "board_calibrate", "name": "Calibrate Board", "icon": "mdi:crosshairs-gps", "endpoint": "config/calibration/auto"},
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the button platform."""
    hub = hass.data[DOMAIN][config_entry.entry_id]
    
    buttons = []
    for button_info in BUTTON_TYPES:
        buttons.append(DartsHubButton(hub, config_entry.entry_id, button_info))
        
    async_add_entities(buttons)

class DartsHubButton(ButtonEntity):
    """Representation of a button that calls the Autodarts API."""

    def __init__(self, hub, entry_id, button_info):
        self._hub = hub
        self._key = button_info["key"]
        self._endpoint = button_info["endpoint"]
        
        self._attr_name = f"Darts Hub {button_info['name']}"
        self._attr_unique_id = f"{entry_id}_{self._key}"
        self._attr_icon = button_info["icon"]

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Darts Hub",
            manufacturer="Autodarts / Darts-hub",
            model="Local WebSocket",
            sw_version="1.1.0",
        )

    async def async_press(self) -> None:
        """Execute the command via the Hub using Autodarts API."""
        await self._hub.send_autodarts_command(self._endpoint)