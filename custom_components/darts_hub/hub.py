import asyncio
import json
import logging
import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

# C'est ce nom exact que Home Assistant cherche !
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
                            
                            # Engine.IO Open (0) -> Send Socket.IO Connect (40)
                            if text.startswith("0"):
                                await ws.send_str("40")
                                continue
                                
                            # Engine.IO Ping (2) -> Send Pong (3)
                            if text == "2":
                                await ws.send_str("3")
                                continue
                                
                            # Socket.IO Connect Auth Success (40)
                            if text.startswith("40"):
                                continue

                            # Socket.IO Event (42)
                            if text.startswith("42"):
                                try:
                                    payload_str = text[2:]
                                    payload = json.loads(payload_str)
                                    
                                    if isinstance(payload, list) and len(payload) >= 2 and payload[0] == "message":
                                        self._dispatch(payload[1])
                                        
                                except json.JSONDecodeError as e:
                                    _LOGGER.error(f"Failed to parse Socket.IO event: {e}")

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