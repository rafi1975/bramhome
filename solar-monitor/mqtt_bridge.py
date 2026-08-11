"""MQTT publisher + optional grid-meter subscriber."""

from __future__ import annotations

import json
import logging
import threading
from typing import Any, Optional

log = logging.getLogger(__name__)


class MqttBridge:
    def __init__(self, cfg: dict) -> None:
        self.enabled = bool(cfg.get("enabled"))
        self.host = cfg.get("host", "127.0.0.1")
        self.port = int(cfg.get("port", 1883))
        self.username = cfg.get("username") or None
        self.password = cfg.get("password") or None
        self.prefix = cfg.get("topic_prefix", "home/solar/solarriver").rstrip("/")
        self.ha_discovery = bool(cfg.get("ha_discovery", True))
        self.device_name = cfg.get("device_name", "SolarRiver 4400TL")
        self._client = None
        self._lock = threading.Lock()
        self._grid_power_w: Optional[float] = None
        self._grid_topic: Optional[str] = None
        self._grid_invert = False
        self._discovery_sent = False

    @property
    def grid_power_w(self) -> Optional[float]:
        with self._lock:
            return self._grid_power_w

    def configure_grid_meter(self, topic: str, invert: bool = False) -> None:
        self._grid_topic = topic
        self._grid_invert = invert

    def start(self) -> None:
        if not self.enabled:
            return
        import paho.mqtt.client as mqtt

        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="solarriver-monitor",
        )
        if self.username:
            self._client.username_pw_set(self.username, self.password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_start()
        log.info("MQTT connected to %s:%s", self.host, self.port)

    def stop(self) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if self._grid_topic:
            client.subscribe(self._grid_topic)
            log.info("Subscribed to grid meter topic %s", self._grid_topic)
        if self.ha_discovery and not self._discovery_sent:
            self._publish_ha_discovery()
            self._discovery_sent = True

    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8").strip()
            # Accept raw number or JSON {"power": 123} / {"value": 123}
            if payload.startswith("{"):
                data = json.loads(payload)
                value = data.get("power", data.get("value", data.get("W")))
            else:
                value = float(payload)
            value = float(value)
            if self._grid_invert:
                value = -value
            with self._lock:
                self._grid_power_w = value
        except Exception:
            log.warning("Could not parse grid meter payload on %s", msg.topic)

    def _publish_ha_discovery(self) -> None:
        device = {
            "identifiers": ["solarriver_4400tl"],
            "name": self.device_name,
            "manufacturer": "Samil Power",
            "model": "SolarRiver 4400TL",
        }
        sensors = [
            ("output_power", "Output Power", "W", "power", "measurement"),
            ("energy_today", "Energy Today", "kWh", "energy", "total_increasing"),
            ("energy_total", "Energy Total", "kWh", "energy", "total_increasing"),
            ("pv_voltage", "PV Voltage", "V", "voltage", "measurement"),
            ("pv_current", "PV Current", "A", "current", "measurement"),
            ("grid_voltage", "Grid Voltage", "V", "voltage", "measurement"),
            ("grid_frequency", "Grid Frequency", "Hz", "frequency", "measurement"),
            ("temperature", "Inverter Temperature", "°C", "temperature", "measurement"),
            ("house_load", "House Load", "W", "power", "measurement"),
            ("grid_power", "Grid Power", "W", "power", "measurement"),
        ]
        binaries = [
            ("producing", "Producing"),
            ("solar_covers_load", "Solar Covers Load"),
            ("exporting", "Exporting"),
        ]
        for key, name, unit, device_class, state_class in sensors:
            payload = {
                "name": name,
                "unique_id": f"solarriver_{key}",
                "state_topic": f"{self.prefix}/state",
                "value_template": f"{{{{ value_json.{key} }}}}",
                "unit_of_measurement": unit,
                "device_class": device_class,
                "state_class": state_class,
                "device": device,
            }
            topic = f"homeassistant/sensor/solarriver_{key}/config"
            self._publish(topic, json.dumps(payload), retain=True)

        for key, name in binaries:
            payload = {
                "name": name,
                "unique_id": f"solarriver_{key}",
                "state_topic": f"{self.prefix}/state",
                "value_template": f"{{{{ value_json.{key} }}}}",
                "payload_on": True,
                "payload_off": False,
                "device": device,
            }
            topic = f"homeassistant/binary_sensor/solarriver_{key}/config"
            self._publish(topic, json.dumps(payload), retain=True)

    def publish_state(self, state: dict[str, Any]) -> None:
        if not self.enabled or not self._client:
            return
        self._publish(f"{self.prefix}/state", json.dumps(state))

    def _publish(self, topic: str, payload: str, retain: bool = False) -> None:
        assert self._client is not None
        self._client.publish(topic, payload, qos=0, retain=retain)
