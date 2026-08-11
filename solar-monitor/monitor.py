#!/usr/bin/env python3
"""SolarRiver 4400TL monitor for Raspberry Pi."""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from pathlib import Path

import yaml

from mqtt_bridge import MqttBridge
from net_power import compute_net_power
from pvoutput_client import PVOutputClient
from samil_protocol import SamilInverter, SamilProtocolError
from storage import ReadingStore

log = logging.getLogger("solar-monitor")
_running = True


def _handle_signal(signum, frame):
    global _running
    log.info("Signal %s received, shutting down", signum)
    _running = False


def load_config(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def once(cfg: dict) -> int:
    serial_cfg = cfg["serial"]
    with SamilInverter(
        port=serial_cfg["port"],
        baud=int(serial_cfg.get("baud", 9600)),
        timeout_s=float(serial_cfg.get("timeout_s", 2.0)),
    ) as inv:
        reading = inv.poll()
    print(yaml.safe_dump(reading.to_dict(), sort_keys=False))
    return 0


def run_loop(cfg: dict) -> int:
    serial_cfg = cfg["serial"]
    poll_cfg = cfg.get("poll", {})
    interval = float(poll_cfg.get("interval_s", 60))
    store = ReadingStore(cfg.get("storage", {}).get("sqlite_path", "readings.db"))

    mqtt = MqttBridge(cfg.get("mqtt", {}))
    grid_cfg = cfg.get("grid_meter", {})
    if grid_cfg.get("enabled"):
        mqtt.configure_grid_meter(
            grid_cfg["mqtt_topic"],
            invert=bool(grid_cfg.get("invert", False)),
        )
    mqtt.start()

    pv = PVOutputClient(cfg.get("pvoutput", {}))
    hysteresis = float(grid_cfg.get("covered_hysteresis_w", 50))

    inv = SamilInverter(
        port=serial_cfg["port"],
        baud=int(serial_cfg.get("baud", 9600)),
        timeout_s=float(serial_cfg.get("timeout_s", 2.0)),
    )
    inv.open()

    try:
        while _running:
            started = time.monotonic()
            try:
                reading = inv.poll()
                grid_w = mqtt.grid_power_w if grid_cfg.get("enabled") else None
                net = compute_net_power(
                    reading.output_power_w,
                    grid_w,
                    hysteresis_w=hysteresis,
                )

                store.insert(
                    reading,
                    grid_power_w=net.grid_power_w,
                    house_load_w=net.house_load_w,
                    solar_covers_load=net.solar_covers_load,
                    exporting=net.exporting,
                )

                state = {
                    "timestamp": reading.timestamp,
                    "output_power": reading.output_power_w,
                    "energy_today": reading.energy_today_kwh,
                    "energy_total": reading.energy_total_kwh,
                    "pv_voltage": reading.pv_voltage_v,
                    "pv_current": reading.pv_current_a,
                    "grid_voltage": reading.grid_voltage_v,
                    "grid_frequency": reading.grid_frequency_hz,
                    "temperature": reading.temperature_c,
                    "mode": reading.mode_name,
                    "producing": reading.producing,
                    "grid_power": net.grid_power_w,
                    "house_load": net.house_load_w,
                    "solar_covers_load": net.solar_covers_load,
                    "exporting": net.exporting,
                    "importing": net.importing,
                }
                mqtt.publish_state(state)
                pv.maybe_upload(reading, grid_power_w=net.grid_power_w)

                log.info(
                    "PV %s W | today %.2f kWh | mode %s | covers=%s export=%s",
                    reading.output_power_w,
                    reading.energy_today_kwh,
                    reading.mode_name,
                    net.solar_covers_load,
                    net.exporting,
                )
            except SamilProtocolError:
                log.exception("Inverter communication error")
            except Exception:
                log.exception("Unexpected error in poll loop")

            elapsed = time.monotonic() - started
            sleep_for = max(1.0, interval - elapsed)
            # Interruptible sleep
            end = time.monotonic() + sleep_for
            while _running and time.monotonic() < end:
                time.sleep(0.2)
    finally:
        inv.close()
        mqtt.stop()
        store.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Monitor Samil Power SolarRiver 4400TL via RS485"
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Poll once and print JSON/YAML, then exit",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Debug logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        log.error(
            "Config not found: %s (copy config.example.yaml to config.yaml)",
            cfg_path,
        )
        return 1

    cfg = load_config(cfg_path)
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if args.once:
        return once(cfg)
    return run_loop(cfg)


if __name__ == "__main__":
    sys.exit(main())
