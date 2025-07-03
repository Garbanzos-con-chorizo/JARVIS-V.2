import json
import os
import threading
from typing import Optional

try:
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover - optional dependency
    mqtt = None


MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
COMMAND_TOPIC = os.environ.get("MQTT_COMMAND_TOPIC", "jarvis/commands")
STATUS_TOPIC = os.environ.get("MQTT_STATUS_TOPIC", "jarvis/status")


class IoTClient:
    """Simple MQTT interface for publishing commands and receiving status."""

    def __init__(self, log_callback=None) -> None:
        self.log_callback = log_callback
        self.status: Optional[str] = None
        if mqtt is None:
            if self.log_callback:
                self.log_callback("paho-mqtt not installed; MQTT disabled.")
            self.client = None
            return

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            threading.Thread(target=self.client.loop_forever, daemon=True).start()
        except Exception as exc:  # pragma: no cover - network dependent
            if self.log_callback:
                self.log_callback(f"MQTT connection error: {exc}")
            self.client = None

    def _on_connect(self, client, userdata, flags, rc) -> None:  # pragma: no cover
        if rc == 0:
            try:
                client.subscribe(STATUS_TOPIC)
            except Exception as exc:
                if self.log_callback:
                    self.log_callback(f"MQTT subscribe error: {exc}")
        else:
            if self.log_callback:
                self.log_callback(f"MQTT connection failed with code {rc}")

    def _on_message(self, client, userdata, msg) -> None:  # pragma: no cover
        try:
            self.status = msg.payload.decode()
        except Exception:
            self.status = str(msg.payload)
        if self.log_callback:
            self.log_callback(f"Status update: {self.status}")

    def publish_command(self, device: str, state: str) -> None:
        """Publish a simple device toggle command."""
        if not self.client:
            return
        payload = json.dumps({"device": device, "state": state})
        try:
            self.client.publish(COMMAND_TOPIC, payload)
        except Exception as exc:  # pragma: no cover - network dependent
            if self.log_callback:
                self.log_callback(f"MQTT publish error: {exc}")

    def get_status(self) -> Optional[str]:
        """Return the most recent status message if available."""
        return self.status
