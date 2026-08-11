"""Derive house-load / solar-covers-load from inverter + grid meter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class NetPowerStatus:
    solar_w: int
    grid_power_w: Optional[float]
    house_load_w: Optional[float]
    solar_covers_load: Optional[bool]
    exporting: Optional[bool]
    importing: Optional[bool]


def compute_net_power(
    solar_w: int,
    grid_power_w: Optional[float],
    hysteresis_w: float = 50.0,
) -> NetPowerStatus:
    """Combine inverter AC output with grid import/export.

    Sign convention for grid_power_w:
      positive = importing from grid
      negative = exporting to grid

    House load ≈ solar_output + grid_import
               = solar_w + grid_power_w
    """
    if grid_power_w is None:
        return NetPowerStatus(
            solar_w=solar_w,
            grid_power_w=None,
            house_load_w=None,
            solar_covers_load=None,
            exporting=None,
            importing=None,
        )

    house = solar_w + grid_power_w
    if house < 0:
        # Measurement noise / CT orientation quirks — clamp
        house = 0.0

    exporting = grid_power_w < -hysteresis_w
    importing = grid_power_w > hysteresis_w
    # Solar covers load when not meaningfully importing from the grid
    solar_covers = solar_w > 0 and not importing

    return NetPowerStatus(
        solar_w=solar_w,
        grid_power_w=round(grid_power_w, 1),
        house_load_w=round(house, 1),
        solar_covers_load=solar_covers,
        exporting=exporting,
        importing=importing,
    )
