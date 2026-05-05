from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

# Define all the sensors we want to extract from the WebSocket JSON
SENSOR_TYPES = [
    {"key": "board_status", "name": "Board Status", "icon": "mdi:target"},
    {"key": "current_event", "name": "Current Event", "icon": "mdi:flash"},
    {"key": "caller", "name": "Caller", "icon": "mdi:account-tie-voice"},
    {"key": "match_id", "name": "Match ID", "icon": "mdi:identifier"},
    {"key": "current_player", "name": "Current Player", "icon": "mdi:account"},
    {"key": "game_mode", "name": "Game Mode", "icon": "mdi:gamepad-variant"},
    {"key": "points_left", "name": "Points Left", "icon": "mdi:numeric"},
    {"key": "last_dart_value", "name": "Last Dart Value", "icon": "mdi:dart"},
    {"key": "last_dart_multiplier", "name": "Last Dart Multiplier", "icon": "mdi:close"},
    {"key": "last_dart_field", "name": "Last Dart Field", "icon": "mdi:bullseye"},
    {"key": "last_dart_type", "name": "Last Dart Type", "icon": "mdi:shape"},
    {"key": "last_dart_x", "name": "Last Dart X", "icon": "mdi:axis-x-arrow"},
    {"key": "last_dart_y", "name": "Last Dart Y", "icon": "mdi:axis-y-arrow"},
    {"key": "round_score", "name": "Round Score", "icon": "mdi:scoreboard"},
]

# Add sensors for up to 6 players remaining scores
for i in range(1, 7):
    SENSOR_TYPES.append({
        "key": f"player{i}_score", 
        "name": f"Player {i} Score", 
        "icon": "mdi:numeric"
    })

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    hub = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = []
    for sensor_info in SENSOR_TYPES:
        sensors.append(DartsHubSensor(hub, config_entry.entry_id, sensor_info))
        
    async_add_entities(sensors)

class DartsHubSensor(SensorEntity):
    """Representation of a Darts Hub Sensor."""

    def __init__(self, hub, entry_id, sensor_info):
        self._hub = hub
        self._key = sensor_info["key"]
        self._attr_name = f"Darts Hub {sensor_info['name']}"
        self._attr_unique_id = f"{entry_id}_{self._key}"
        self._attr_icon = sensor_info["icon"]
        self._state = None
        self._remove_callback = None

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        self._remove_callback = self._hub.register_callback(self._handle_new_data)

    async def async_will_remove_from_hass(self):
        """Run when entity will be removed from hass."""
        if self._remove_callback:
            self._remove_callback()

    def _handle_new_data(self, data):
        """Process incoming WebSocket data and update the specific sensor state."""
        event = data.get("event")
        updated = False

        if self._key == "current_event":
            self._state = event
            updated = True
        elif self._key == "board_status" and event == "Board Status":
            self._state = data.get("data", {}).get("status", self._state)
            updated = True
        elif self._key == "caller" and event == "welcome":
            self._state = data.get("caller", self._state)
            updated = True
        elif self._key == "match_id" and event == "match-started":
            self._state = data.get("id", self._state)
            updated = True
        elif self._key == "current_player" and "player" in data:
            self._state = data.get("player")
            updated = True
        elif self._key == "game_mode" and "game" in data:
            self._state = data["game"].get("mode", self._state)
            updated = True
        elif self._key == "points_left" and "game" in data and "pointsLeft" in data["game"]:
            self._state = data["game"]["pointsLeft"]
            updated = True
        elif self._key == "last_dart_value" and "game" in data and "dartValue" in data["game"]:
            self._state = data["game"]["dartValue"]
            updated = True
        elif self._key == "last_dart_multiplier" and "game" in data and "fieldMultiplier" in data["game"]:
            self._state = data["game"]["fieldMultiplier"]
            updated = True
        elif self._key == "last_dart_field" and "game" in data and "fieldName" in data["game"]:
            self._state = data["game"]["fieldName"]
            updated = True
        elif self._key == "last_dart_type" and "game" in data and "type" in data["game"]:
            self._state = data["game"]["type"]
            updated = True
        elif self._key == "last_dart_x" and "game" in data and "coords" in data["game"]:
            self._state = round(data["game"]["coords"].get("x", 0), 4)
            updated = True
        elif self._key == "last_dart_y" and "game" in data and "coords" in data["game"]:
            self._state = round(data["game"]["coords"].get("y", 0), 4)
            updated = True
        elif self._key == "round_score" and "game" in data and "dartsThrownValue" in data["game"]:
            self._state = data["game"]["dartsThrownValue"]
            updated = True
        elif self._key.endswith("_score") and self._key.startswith("player") and "remainingScores" in data:
            json_key = self._key.replace("_score", "")
            if json_key in data["remainingScores"]:
                self._state = data["remainingScores"][json_key]
                updated = True

        if updated:
            self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the current state."""
        return self._state

    @property
    def should_poll(self):
        """No polling needed. Updates are pushed via WebSockets."""
        return False