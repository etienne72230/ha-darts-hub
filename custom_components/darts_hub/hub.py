import asyncio
import json
import logging
import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class DartsHubWebSocket:
    """Manage the WebSocket and API connections to Darts-hub and Autodarts."""

    def __init__(self, hass, host, port, autodarts_port):
        self.hass = hass
        self.host = host
        self.port = port
        self.autodarts_port = autodarts_port
        self.url_hub = f"wss://{host}:{port}/socket.io/?transport=websocket&EIO=4"
        self.url_autodarts_ws = f"ws://{host}:{autodarts_port}/api/events"
        self.url_autodarts_http = f"http://{host}:{autodarts_port}/api"
        self._callbacks = set()
        self.connected = False

    def register_callback(self, callback):
        """Register a callback to receive data updates."""
        self._callbacks.add(callback)
        return lambda: self._callbacks.discard(callback)

    async def connect(self):
        """Initialize background listeners."""
        self.hass.loop.create_task(self._listen_hub())
        self.hass.loop.create_task(self._listen_autodarts())

    async def send_autodarts_command(self, endpoint: str):
        """Send a POST command directly to the Autodarts local API."""
        session = async_get_clientsession(self.hass)
        url = f"{self.url_autodarts_http}/{endpoint}"
        try:
            async with session.post(url, timeout=5) as resp:
                if resp.status == 200:
                    _LOGGER.info(f"Autodarts command '{endpoint}' executed successfully.")
                else:
                    _LOGGER.error(f"Autodarts command '{endpoint}' failed with status {resp.status}")
        except Exception as e:
            _LOGGER.error(f"Error communicating with Autodarts API: {e}")

    async def _listen_hub(self):
        """Listen to Darts-hub for match data (Socket.IO)."""
        session = async_get_clientsession(self.hass)
        while True:
            try:
                async with session.ws_connect(self.url_hub, ssl=False) as ws:
                    self.connected = True
                    self._dispatch({"internal_event": "connection_state", "connected": True})
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            if msg.data.startswith("0"): await ws.send_str("40")
                            elif msg.data == "2": await ws.send_str("3")
                            elif msg.data.startswith("42"):
                                payload = json.loads(msg.data[2:])
                                if payload[0] == "message":
                                    payload[1]["source"] = "dart-hub"
                                    self._dispatch(payload[1])
            except Exception as e:
                _LOGGER.error(f"Darts-hub connection error: {e}")
            
            if self.connected:
                self.connected = False
                self._dispatch({"internal_event": "connection_state", "connected": False})
            await asyncio.sleep(10)

    async def _listen_autodarts(self):
        """Listen to Autodarts raw events to trigger state updates."""
        session = async_get_clientsession(self.hass)
        while True:
            try:
                async with session.ws_connect(self.url_autodarts_ws) as ws:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if data.get("type") in ["motion_state", "board_state"]:
                                await self._fetch_autodarts_state(session)
            except Exception as e:
                _LOGGER.debug(f"Autodarts event listener silent: {e}")
            await asyncio.sleep(10)

    async def _fetch_autodarts_state(self, session):
        """Fetch Autodarts state and map it to sensors."""
        try:
            async with session.get(f"{self.url_autodarts_http}/state", timeout=2) as resp:
                if resp.status == 200:
                    state = await resp.json()
                    event_type = state.get("event")
                    if event_type == "Throw detected" and state.get("numThrows", 0) > 0:
                        num = state["numThrows"]
                        last_throw = state["throws"][-1]
                        mapped = {
                            "event": f"dart{num}-thrown",
                            "source": "autodarts_raw",
                            "game": {
                                "dartValue": last_throw["segment"]["number"],
                                "fieldName": str(last_throw["segment"]["name"]).upper(),
                                "fieldMultiplier": last_throw["segment"]["multiplier"],
                                "coords": last_throw["coords"],
                                "type": last_throw["segment"]["bed"].lower(),
                                "pointsLeft": 0
                            }
                        }
                        self._dispatch(mapped)
                    elif event_type == "Takeout started":
                        self._dispatch({"event": "darts-pulled", "source": "autodarts_raw"})
        except Exception: pass

    def _dispatch(self, data):
        """Dispatch data to all registered entities."""
        for callback in self._callbacks:
            callback(data)