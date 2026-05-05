import asyncio
import json
import logging
import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class DartsHubWebSocket:
    """Manage the WebSocket connection to Dart-Hub."""

    def __init__(self, hass, host, port):
        self.hass = hass
        self.host = host
        self.port = port
        self.url = f"wss://{host}:{port}/socket.io/?transport=websocket&EIO=4"
        self._callbacks = set()
        self._loop_task = None

    def register_callback(self, callback):
        """Register a callback to receive WebSocket updates."""
        self._callbacks.add(callback)
        def remove_callback():
            self._callbacks.discard(callback)
        return remove_callback

    async def connect(self):
        """Start the background listening task."""
        self._loop_task = self.hass.loop.create_task(self._listen())

    async def _listen(self):
        """Main loop to listen to the WebSocket."""
        session = async_get_clientsession(self.hass)
        
        while True:
            try:
                # ssl=False is required because local WebSocket servers usually have self-signed certificates
                async with session.ws_connect(self.url, ssl=False) as ws:
                    _LOGGER.info("Connected to Darts Hub WebSocket")
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            text = msg.data
                            
                            # Handle Engine.IO ping/pong heartbeat
                            if text == "2":
                                await ws.send_str("3")
                                continue
                            if text == "ping":
                                await ws.send_str("pong")
                                continue

                            # Parse Socket.IO messages containing arrays (e.g., 2["message", {...}])
                            if '["message",' in text:
                                start_idx = text.find("[")
                                if start_idx != -1:
                                    try:
                                        payload = json.loads(text[start_idx:])
                                        if len(payload) >= 2 and payload[0] == "message":
                                            self._dispatch(payload[1])
                                    except json.JSONDecodeError:
                                        pass

                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
            except Exception as e:
                _LOGGER.error(f"Darts Hub WebSocket error: {e}")
            
            # Reconnect delay after a failure or disconnection
            await asyncio.sleep(5)

    def _dispatch(self, data):
        """Send the parsed JSON dictionary to all registered sensors."""
        for callback in self._callbacks:
            callback(data)