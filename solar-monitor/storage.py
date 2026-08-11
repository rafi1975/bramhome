"""SQLite storage for inverter readings."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Optional

from samil_protocol import InverterReading


SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    temperature_c REAL,
    pv_voltage_v REAL,
    pv_current_a REAL,
    operating_hours_h REAL,
    mode INTEGER,
    mode_name TEXT,
    energy_today_kwh REAL,
    grid_current_a REAL,
    grid_voltage_v REAL,
    grid_frequency_hz REAL,
    output_power_w INTEGER,
    energy_total_kwh REAL,
    producing INTEGER,
    grid_power_w REAL,
    house_load_w REAL,
    solar_covers_load INTEGER,
    exporting INTEGER
);

CREATE INDEX IF NOT EXISTS idx_readings_ts ON readings(ts);
"""


class ReadingStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def insert(
        self,
        reading: InverterReading,
        grid_power_w: Optional[float] = None,
        house_load_w: Optional[float] = None,
        solar_covers_load: Optional[bool] = None,
        exporting: Optional[bool] = None,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO readings (
                ts, temperature_c, pv_voltage_v, pv_current_a, operating_hours_h,
                mode, mode_name, energy_today_kwh, grid_current_a, grid_voltage_v,
                grid_frequency_hz, output_power_w, energy_total_kwh, producing,
                grid_power_w, house_load_w, solar_covers_load, exporting
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                reading.timestamp,
                reading.temperature_c,
                reading.pv_voltage_v,
                reading.pv_current_a,
                reading.operating_hours_h,
                reading.mode,
                reading.mode_name,
                reading.energy_today_kwh,
                reading.grid_current_a,
                reading.grid_voltage_v,
                reading.grid_frequency_hz,
                reading.output_power_w,
                reading.energy_total_kwh,
                int(reading.producing),
                grid_power_w,
                house_load_w,
                None if solar_covers_load is None else int(solar_covers_load),
                None if exporting is None else int(exporting),
            ),
        )
        self._conn.commit()

    def recent(self, limit: int = 20) -> list[dict]:
        cur = self._conn.execute(
            """
            SELECT ts, output_power_w, energy_today_kwh, mode_name, producing,
                   grid_power_w, house_load_w, solar_covers_load, exporting
            FROM readings
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        cols = [d[0] for d in cur.description]
        rows = []
        for row in cur.fetchall():
            item = dict(zip(cols, row))
            item["ts_iso"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(item["ts"])
            )
            rows.append(item)
        return rows
