from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

# Core sensors
SENSOR_TYPES = [
    {"key": "board_status", "name": "Board Status", "icon": "mdi:target", "default": "Waiting..."},
    {"key": "current_event", "name": "Current Event", "icon": "mdi:flash", "default": "Waiting..."},
    {"key": "match_id", "name": "Match ID", "icon": "mdi:identifier", "default": "None"},
    {"key": "current_player", "name": "Current Player", "icon": "mdi:account-star", "default": "Waiting..."},
    {"key": "game_mode", "name": "Game Mode", "icon": "mdi:gamepad-variant", "default": "Unknown"},
    {"key": "points_left", "name": "Points Left", "icon": "mdi:numeric", "default": 0},
    {"key": "round_score", "name": "Round Score", "icon": "mdi:scoreboard", "default": 0},
]

# Add sensors for Dart 1, Dart 2, Dart 3, and Last Dart
for prefix in ["dart1", "dart2", "dart3", "last_dart"]:
    name_prefix = prefix.replace('_', ' ').title()
    SENSOR_TYPES.extend([
        {"key": f"{prefix}_value", "name": f"{name_prefix} Value", "icon": "mdi:dart", "default": 0},
        {"key": f"{prefix}_multiplier", "name": f"{name_prefix} Multiplier", "icon": "mdi:close", "default": 0},
        {"key": f"{prefix}_field", "name": f"{name_prefix} Field", "icon": "mdi:bullseye", "default": "-"},
        {"key": f"{prefix}_type", "name": f"{name_prefix} Type", "icon": "mdi:shape", "default": "-"},
        {"key": f"{prefix}_x", "name": f"{name_prefix} X", "icon": "mdi:axis-x-arrow", "default": 0.0},
        {"key": f"{prefix}_y", "name": f"{name_prefix} Y", "icon": "mdi:axis-y-arrow", "default": 0.0},
    ])

# Add sensors for Player Scores and Player Names (up to 6 players)
for i in range(1, 7):
    SENSOR_TYPES.extend([
        {"key": f"player{i}_score", "name": f"Player {i} Score", "icon": "mdi:numeric", "default": 0},
        {"key": f"player{i}_name", "name": f"Player {i} Name", "icon": "mdi:account", "default": "Waiting..."}
    ])

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
        self._state = sensor_info.get("default", None)
        self._remove_callback = None

        # Link this entity to the Darts Hub device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Darts Hub",
            manufacturer="Autodarts / Darts-hub",
            model="Local WebSocket",
            sw_version="1.0.0",
        )

    async def async_added_to_hass(self):
        """Register the callback when the entity is added to Home Assistant."""
        self._remove_callback = self._hub.register_callback(self._handle_new_data)

    async def async_will_remove_from_hass(self):
        """Clean up the callback when the entity is removed."""
        if self._remove_callback:
            self._remove_callback()

    def _handle_new_data(self, data):
        """Process incoming WebSocket data and update the specific sensor state."""
        event = data.get("event")
        game = data.get("game", {})
        updated = False

        if self._key == "current_event":
            self._state = event
            updated = True

        elif self._key == "board_status" and event == "Board Status":
            self._state = data.get("data", {}).get("status", self._state)
            updated = True

        elif self._key == "match_id" and event == "match-started":
            self._state = data.get("id", self._state)
            updated = True

        elif self._key == "game_mode" and "mode" in game:
            self._state = game["mode"]
            updated = True

        elif self._key == "points_left" and "pointsLeft" in game:
            self._state = game["pointsLeft"]
            updated = True

        elif self._key == "round_score" and "dartsThrownValue" in game:
            self._state = game["dartsThrownValue"]
            updated = True

        # Handle Current Player and Player Names tracking
        elif self._key == "current_player" or self._key.endswith("_name"):
            if "player" in data and "playerIndex" in data:
                # Darts-hub playerIndex starts at 0, so we add 1 for "Player 1"
                current_idx = str(int(data["playerIndex"]) + 1)
                if self._key == "current_player" or self._key == f"player{current_idx}_name":
                    self._state = data["player"]
                    updated = True

        # Handle Player Scores
        elif self._key.endswith("_score") and self._key.startswith("player"):
            if "remainingScores" in data:
                json_key = self._key.replace("_score", "")
                if json_key in data["remainingScores"]:
                    self._state = data["remainingScores"][json_key]
                    updated = True

        # Handle Darts Data (Dart 1, 2, 3 and Last Dart)
        elif self._key.startswith("dart") or self._key.startswith("last_dart"):
            dart_events = ["dart1-thrown", "dart2-thrown", "dart3-thrown"]
            
            # UX Improvement: Reset Dart 2 and Dart 3 data when a new round starts (Dart 1 is thrown)
            if event == "dart1-thrown" and (self._key.startswith("dart2_") or self._key.startswith("dart3_")):
                if self._key.endswith(("_value", "_multiplier", "_x", "_y")):
                    self._state = 0
                else:
                    self._state = "-"
                updated = True

            elif event in dart_events:
                dart_prefix = event.split('-')[0] # Extracts "dart1", "dart2", or "dart3"
                
                # Check if this sensor matches the current dart thrown OR if it is the last_dart tracker
                if self._key.startswith(f"{dart_prefix}_") or self._key.startswith("last_dart_"):
                    if self._key.endswith("_value") and "dartValue" in game:
                        self._state = game["dartValue"]
                        updated = True
                    elif self._key.endswith("_multiplier") and "fieldMultiplier" in game:
                        self._state = game["fieldMultiplier"]
                        updated = True
                    elif self._key.endswith("_field") and "fieldName" in game:
                        self._state = game["fieldName"]
                        updated = True
                    elif self._key.endswith("_type") and "type" in game:
                        self._state = game["type"]
                        updated = True
                    elif self._key.endswith("_x") and "coords" in game:
                        self._state = round(game["coords"].get("x", 0), 4)
                        updated = True
                    elif self._key.endswith("_y") and "coords" in game:
                        self._state = round(game["coords"].get("y", 0), 4)
                        updated = True

        # Notify Home Assistant that the state has changed
        if updated:
            self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the current state."""
        return self._state

    @property
    def should_poll(self):
        """Disable polling. Updates are pushed directly via WebSockets."""
        return False