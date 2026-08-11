"""Optional PVOutput.org uploader."""

from __future__ import annotations

import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Optional

from samil_protocol import InverterReading

log = logging.getLogger(__name__)


class PVOutputClient:
    def __init__(self, cfg: dict) -> None:
        self.enabled = bool(cfg.get("enabled"))
        self.api_key = cfg.get("api_key", "")
        self.system_id = str(cfg.get("system_id", ""))
        self.min_interval_s = int(cfg.get("min_interval_s", 300))
        self._last_upload = 0.0

    def maybe_upload(
        self,
        reading: InverterReading,
        grid_power_w: Optional[float] = None,
    ) -> None:
        if not self.enabled:
            return
        now = time.time()
        if now - self._last_upload < self.min_interval_s:
            return

        local = datetime.fromtimestamp(reading.timestamp)
        fields = {
            "d": local.strftime("%Y%m%d"),
            "t": local.strftime("%H:%M"),
            "v1": int(reading.energy_today_kwh * 1000),  # Wh generation
            "v2": int(reading.output_power_w),  # W power
            "v5": reading.temperature_c,
            "v6": reading.pv_voltage_v,
            "c1": 0,
            "n": 0,
        }
        # v4 = power consumption if we know house load
        if grid_power_w is not None:
            # house load = solar + grid_import (grid positive = import)
            house = reading.output_power_w + grid_power_w
            if house < 0:
                house = 0
            fields["v4"] = int(house)

        data = urllib.parse.urlencode(fields).encode("utf-8")
        req = urllib.request.Request(
            "https://pvoutput.org/service/r2/addstatus.jsp",
            data=data,
            headers={
                "X-Pvoutput-Apikey": self.api_key,
                "X-Pvoutput-SystemId": self.system_id,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                log.info("PVOutput upload OK: %s", body.strip())
                self._last_upload = now
        except urllib.error.HTTPError as exc:
            log.error("PVOutput HTTP %s: %s", exc.code, exc.read().decode())
        except Exception:
            log.exception("PVOutput upload failed")
