"""Unit tests that do not need hardware."""

from __future__ import annotations

import struct
import unittest

from net_power import compute_net_power
from samil_protocol import HEADER, SamilInverter


class NetPowerTests(unittest.TestCase):
    def test_importing(self):
        # 800 W solar, 1200 W house -> import 400 W
        net = compute_net_power(800, 400)
        self.assertEqual(net.house_load_w, 1200.0)
        self.assertTrue(net.importing)
        self.assertFalse(net.exporting)
        self.assertFalse(net.solar_covers_load)

    def test_exporting(self):
        # 2000 W solar, 500 W house -> export 1500 W
        net = compute_net_power(2000, -1500)
        self.assertEqual(net.house_load_w, 500.0)
        self.assertTrue(net.exporting)
        self.assertFalse(net.importing)
        self.assertTrue(net.solar_covers_load)

    def test_covered_at_zero_export(self):
        net = compute_net_power(600, 0)
        self.assertEqual(net.house_load_w, 600.0)
        self.assertTrue(net.solar_covers_load)
        self.assertFalse(net.exporting)
        self.assertFalse(net.importing)

    def test_no_grid_meter(self):
        net = compute_net_power(1000, None)
        self.assertIsNone(net.house_load_w)
        self.assertIsNone(net.solar_covers_load)


class ProtocolPacketTests(unittest.TestCase):
    def test_checksum_and_build(self):
        inv = SamilInverter("/dev/null")
        pkt = inv._build_packet(0, 0, 0x00, 0x04)
        self.assertTrue(pkt.startswith(HEADER))
        body, ck = pkt[:-2], pkt[-2:]
        self.assertEqual(struct.unpack(">H", ck)[0], sum(body) & 0xFFFF)
        # 55 aa 00 00 00 00 00 04 00 + checksum
        self.assertEqual(len(pkt), 11)

    def test_parse_status_layout(self):
        inv = SamilInverter("/dev/null")
        # Build a synthetic status payload matching the documented offsets
        data = bytearray(36)
        struct.pack_into(">H", data, 0, 351)  # 35.1 C
        struct.pack_into(">H", data, 2, 3205)  # 320.5 V
        struct.pack_into(">H", data, 4, 45)  # 4.5 A
        struct.pack_into(">I", data, 6, 12345)  # hours *10
        struct.pack_into(">H", data, 10, 1)  # normal
        struct.pack_into(">H", data, 12, 1234)  # 12.34 kWh today
        struct.pack_into(">H", data, 24, 50)  # 5.0 A grid
        struct.pack_into(">H", data, 26, 2305)  # 230.5 V
        struct.pack_into(">H", data, 28, 5001)  # 50.01 Hz
        struct.pack_into(">H", data, 30, 1420)  # 1420 W
        struct.pack_into(">I", data, 32, 98765)  # 9876.5 kWh total

        reading = inv._parse_status(bytes(data))
        self.assertEqual(reading.temperature_c, 35.1)
        self.assertEqual(reading.pv_voltage_v, 320.5)
        self.assertEqual(reading.pv_current_a, 4.5)
        self.assertEqual(reading.mode_name, "normal")
        self.assertEqual(reading.energy_today_kwh, 12.34)
        self.assertEqual(reading.grid_voltage_v, 230.5)
        self.assertEqual(reading.grid_frequency_hz, 50.01)
        self.assertEqual(reading.output_power_w, 1420)
        self.assertEqual(reading.energy_total_kwh, 9876.5)
        self.assertTrue(reading.producing)


if __name__ == "__main__":
    unittest.main()
