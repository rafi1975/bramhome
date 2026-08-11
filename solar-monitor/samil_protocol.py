"""Samil Power SolarRiver TL RS485 protocol (9600 8N1).

Packet format (same family as GoodWe/SolarRiver proprietary framing):
  55 AA | src(2) | dst(2) | ctrl(1) | func(1) | len(1) | data(len) | checksum(2)

Checksum is the sum of all preceding bytes, big-endian uint16.

Discovery / read sequence (from field-tested 4400TL implementations):
  1. Broadcast re-register  ctrl=0x00 func=0x04
  2. Offline query          ctrl=0x00 func=0x00  -> serial (func 0x80)
  3. Register serial        ctrl=0x00 func=0x01  -> address (func 0x81)
  4. Request status         ctrl=0x01 func=0x02  -> status  (func 0x82)
"""

from __future__ import annotations

import logging
import struct
import time
from dataclasses import asdict, dataclass
from typing import Optional

import serial

log = logging.getLogger(__name__)

HEADER = b"\x55\xaa"


@dataclass
class InverterReading:
    timestamp: float
    temperature_c: float
    pv_voltage_v: float
    pv_current_a: float
    operating_hours_h: float
    mode: int
    energy_today_kwh: float
    grid_current_a: float
    grid_voltage_v: float
    grid_frequency_hz: float
    output_power_w: int
    energy_total_kwh: float
    producing: bool
    mode_name: str

    def to_dict(self) -> dict:
        return asdict(self)


MODE_NAMES = {
    0: "waiting",
    1: "normal",
    2: "fault",
    3: "permanent_fault",
    4: "check",
    5: "off",
}


class SamilProtocolError(Exception):
    pass


class SamilInverter:
    def __init__(
        self,
        port: str,
        baud: int = 9600,
        timeout_s: float = 2.0,
    ) -> None:
        self.port = port
        self.baud = baud
        self.timeout_s = timeout_s
        self._ser: Optional[serial.Serial] = None
        self._address: int = 0
        self._serial_number: str = ""

    def open(self) -> None:
        self._ser = serial.Serial(
            port=self.port,
            baudrate=self.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout_s,
        )
        # Give USB adapters a moment after open
        time.sleep(0.2)
        self._ser.reset_input_buffer()

    def close(self) -> None:
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None

    def __enter__(self) -> "SamilInverter":
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @property
    def serial_number(self) -> str:
        return self._serial_number

    @property
    def address(self) -> int:
        return self._address

    def _checksum(self, payload: bytes) -> bytes:
        return struct.pack(">H", sum(payload) & 0xFFFF)

    def _build_packet(
        self,
        src: int,
        dst: int,
        ctrl: int,
        func: int,
        data: bytes = b"",
    ) -> bytes:
        body = HEADER + struct.pack(
            ">HHBBB",
            src & 0xFFFF,
            dst & 0xFFFF,
            ctrl & 0xFF,
            func & 0xFF,
            len(data) & 0xFF,
        ) + data
        return body + self._checksum(body)

    def _write(self, packet: bytes) -> None:
        assert self._ser is not None
        log.debug("TX %s", packet.hex(" "))
        self._ser.reset_input_buffer()
        self._ser.write(packet)
        self._ser.flush()

    def _read_packet(self, deadline: float) -> bytes:
        assert self._ser is not None
        buf = bytearray()
        state = 0
        length = 0

        while time.monotonic() < deadline:
            chunk = self._ser.read(1)
            if not chunk:
                continue
            b = chunk[0]

            if state == 0:
                if b == 0x55:
                    buf = bytearray([b])
                    state = 1
                continue

            if state == 1:
                if b == 0xAA:
                    buf.append(b)
                    state = 2
                elif b == 0x55:
                    buf = bytearray([b])
                else:
                    state = 0
                    buf.clear()
                continue

            buf.append(b)

            # After header we need src/dst/ctrl/func/len = 7 more bytes
            # before knowing full size. Index of len byte is 8.
            if state < 9:
                state += 1
                if state == 9:
                    length = b
                continue

            # Full frame: 9 header bytes + data + 2 checksum
            expected = 9 + length + 2
            if len(buf) >= expected:
                frame = bytes(buf[:expected])
                data_part = frame[:-2]
                ck_rx = struct.unpack(">H", frame[-2:])[0]
                ck_calc = sum(data_part) & 0xFFFF
                if ck_rx != ck_calc:
                    raise SamilProtocolError(
                        f"bad checksum rx={ck_rx:#06x} calc={ck_calc:#06x}"
                    )
                log.debug("RX %s", frame.hex(" "))
                return frame

        raise SamilProtocolError("timeout waiting for inverter response")

    def _transact(
        self,
        src: int,
        dst: int,
        ctrl: int,
        func: int,
        data: bytes = b"",
        expect_ctrl: Optional[int] = None,
        expect_func: Optional[int] = None,
        wait_s: Optional[float] = None,
    ) -> bytes:
        packet = self._build_packet(src, dst, ctrl, func, data)
        self._write(packet)
        # Inverter often needs a short bus settle after TX
        time.sleep(0.05)
        deadline = time.monotonic() + (wait_s or self.timeout_s)
        frame = self._read_packet(deadline)
        rx_ctrl = frame[6]
        rx_func = frame[7]
        if expect_ctrl is not None and rx_ctrl != expect_ctrl:
            raise SamilProtocolError(
                f"unexpected ctrl {rx_ctrl:#04x}, wanted {expect_ctrl:#04x}"
            )
        if expect_func is not None and rx_func != expect_func:
            raise SamilProtocolError(
                f"unexpected func {rx_func:#04x}, wanted {expect_func:#04x}"
            )
        return frame

    def discover(self) -> str:
        """Re-register and return inverter serial number."""
        # Broadcast: ask devices to re-register
        self._write(self._build_packet(0, 0, 0x00, 0x04))
        time.sleep(2.0)

        # Offline query — inverter replies with serial (ctrl=0x00, func=0x80)
        frame = self._transact(
            0,
            0,
            0x00,
            0x00,
            expect_ctrl=0x00,
            expect_func=0x80,
            wait_s=max(3.0, self.timeout_s),
        )
        data_len = frame[8]
        serial_bytes = frame[9 : 9 + data_len]
        serial_number = serial_bytes.decode("ascii", errors="ignore").strip("\x00 ")
        self._serial_number = serial_number
        log.info("Found inverter serial %s", serial_number)

        # Register serial -> receive assigned address (func 0x81)
        time.sleep(0.2)
        frame = self._transact(
            0,
            0,
            0x00,
            0x01,
            serial_bytes,
            expect_ctrl=0x00,
            expect_func=0x81,
            wait_s=max(3.0, self.timeout_s),
        )
        self._address = (frame[2] << 8) | frame[3]
        log.info("Inverter address %#04x", self._address)
        return serial_number

    def read_status(self) -> InverterReading:
        if not self._address:
            self.discover()

        time.sleep(0.2)
        frame = self._transact(
            0,
            self._address,
            0x01,
            0x02,
            expect_ctrl=0x01,
            expect_func=0x82,
            wait_s=max(3.0, self.timeout_s),
        )
        data = frame[9 : 9 + frame[8]]
        return self._parse_status(data)

    def _u16(self, data: bytes, offset: int) -> int:
        return struct.unpack_from(">H", data, offset)[0]

    def _u32(self, data: bytes, offset: int) -> int:
        return struct.unpack_from(">I", data, offset)[0]

    def _parse_status(self, data: bytes) -> InverterReading:
        # Layout validated against Hugo Fiennes' 4400TL Electric Imp reader
        # and community SolarRiver TL parsers.
        if len(data) < 36:
            raise SamilProtocolError(f"status payload too short: {len(data)} bytes")

        temperature = self._u16(data, 0) * 0.1
        pv_voltage = self._u16(data, 2) * 0.1
        pv_current = self._u16(data, 4) * 0.1
        operating_hours = self._u32(data, 6) * 0.1
        mode = self._u16(data, 10)
        energy_today = self._u16(data, 12) * 0.01
        # offsets 14..23 are reserved / unused on this model family
        grid_current = self._u16(data, 24) * 0.1
        grid_voltage = self._u16(data, 26) * 0.1
        grid_frequency = self._u16(data, 28) * 0.01
        output_power = self._u16(data, 30)
        energy_total = self._u32(data, 32) * 0.1

        mode_name = MODE_NAMES.get(mode, f"unknown_{mode}")
        producing = output_power > 0 and mode_name == "normal"

        return InverterReading(
            timestamp=time.time(),
            temperature_c=round(temperature, 1),
            pv_voltage_v=round(pv_voltage, 1),
            pv_current_a=round(pv_current, 1),
            operating_hours_h=round(operating_hours, 1),
            mode=mode,
            energy_today_kwh=round(energy_today, 2),
            grid_current_a=round(grid_current, 1),
            grid_voltage_v=round(grid_voltage, 1),
            grid_frequency_hz=round(grid_frequency, 2),
            output_power_w=int(output_power),
            energy_total_kwh=round(energy_total, 1),
            producing=producing,
            mode_name=mode_name,
        )

    def poll(self) -> InverterReading:
        """Discover if needed, then read status. Retries discovery on failure."""
        try:
            return self.read_status()
        except SamilProtocolError:
            log.warning("Status read failed; rediscovering inverter", exc_info=True)
            self._address = 0
            self.discover()
            return self.read_status()
