# SolarRiver 4400TL monitor (Raspberry Pi)

Poll a **Samil Power SolarRiver 4400TL** over **RS485**, store stats, and optionally publish to MQTT / PVOutput.

Your Pi 3 is a good fit for this.

## Important: “when it takes over from the grid”

The SolarRiver 4400TL is a **grid-tied** inverter. It does **not** island your house or switch the grid off.

- Solar AC is injected **in parallel** with the grid.
- House loads take solar first; any shortfall comes from the grid; any surplus is exported.
- The inverter alone can tell you **when it is producing** and **how many watts**.
- To know **when solar is covering the house** (vs still importing), you also need a **grid import/export meter** (CT clamp), e.g. Shelly EM, SDM120, IoTaWatt.

This project supports both: inverter RS485 + optional MQTT grid-power topic.

```
  PV panels ──► SolarRiver 4400TL ──► house AC bus ◄── grid
                      │                      │
                   RS485                CT on grid feed
                      │                      │
                 Raspberry Pi 3 ◄──── Shelly EM / meter (MQTT)
```

## What you get from the inverter

| Field | Meaning |
| --- | --- |
| `output_power_w` | Instant AC production (W) |
| `energy_today_kwh` / `energy_total_kwh` | Daily / lifetime yield |
| `pv_voltage_v` / `pv_current_a` | DC string |
| `grid_voltage_v` / `grid_frequency_hz` | AC grid side |
| `temperature_c` | Inverter temp |
| `mode_name` | waiting / normal / fault / … |
| `producing` | `true` when mode is normal and power > 0 |

With a grid meter attached:

| Field | Meaning |
| --- | --- |
| `house_load_w` | ≈ solar + grid_import |
| `solar_covers_load` | producing and not importing |
| `exporting` / `importing` | based on grid meter sign |

## Hardware

| Item | Notes |
| --- | --- |
| Raspberry Pi 3 (any) | Wi-Fi or Ethernet to your LAN |
| **Isolated** USB↔RS485 adapter | Prefer galvanically isolated (EMI near inverters) |
| Cable to inverter RS485 | Often RJ11/RJ45 style port on SolarRiver — check your manual for A/B pins |
| 5 V PSU for the Pi | Official or quality 2.5 A+ supply |
| Optional: Shelly EM / SDM120 | Grid CT for import/export |

### Wiring tips

1. Power off AC/DC before opening the inverter communication cover.
2. Connect RS485 **A/B** (and GND if your adapter has it) to the inverter COM port. If nothing answers, swap A/B — that is the most common fix.
3. Keep the RS485 run reasonably short; use twisted pair.
4. On the Pi: adapter usually appears as `/dev/ttyUSB0`. Add your user to `dialout`:
   ```bash
   sudo usermod -aG dialout $USER
   ```
5. Prefer an **isolated** USB-RS485 dongle; non-isolated ones often drop frames near inverters.

## Software setup (Pi OS)

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git
cd ~
git clone <this-repo> bramhome
cd bramhome/solar-monitor

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp config.example.yaml config.yaml
# edit serial.port, mqtt, pvoutput, grid_meter as needed
mkdir -p /var/lib/solar-monitor   # or change storage.sqlite_path to ./data/readings.db
```

### One-shot test (while the inverter is awake / daytime)

```bash
python monitor.py -c config.yaml --once -v
```

### Continuous logging

```bash
python monitor.py -c config.yaml
```

### systemd

```bash
sudo cp deploy/solar-monitor.service /etc/systemd/system/
# edit paths/user if needed
sudo systemctl daemon-reload
sudo systemctl enable --now solar-monitor
journalctl -u solar-monitor -f
```

## MQTT / Home Assistant

Enable in `config.yaml`:

```yaml
mqtt:
  enabled: true
  host: 192.168.1.10
  topic_prefix: home/solar/solarriver
  ha_discovery: true
```

State is published as JSON on `home/solar/solarriver/state`. With `ha_discovery: true`, sensors appear automatically in Home Assistant.

### Grid meter for “solar covers load”

Point `grid_meter.mqtt_topic` at a topic that publishes **watts**, with:

- **positive** = importing from grid  
- **negative** = exporting to grid  

(set `invert: true` if your meter is flipped).

Example Shelly EM style topic (adjust to your device):

```yaml
grid_meter:
  enabled: true
  mqtt_topic: shellies/shellyem-XXXX/emeter/0/power
  invert: false
```

## PVOutput.org

Create a free system, put API key + system id in config, set `enabled: true`. Uploads respect the 5-minute minimum.

## Protocol notes

Framing is the SolarRiver / GoodWe-style `55 AA` binary protocol at **9600 8N1**, not Modbus. Discovery:

1. Broadcast re-register (`ctrl=0x00`, `func=0x04`)
2. Offline query (`0x00/0x00`) → serial (`0x80`)
3. Register serial (`0x00/0x01`) → address (`0x81`)
4. Status request (`0x01/0x02`) → status (`0x82`)

Status field layout matches field-tested SolarRiver 4400TL readers (e.g. Hugo Fiennes’ Electric Imp logger).

## Alternatives

| Project | When to use |
| --- | --- |
| [vk2tds/SamilLogger](https://github.com/vk2tds/SamilLogger) | ESP8266 instead of Pi |
| [mhvis/solar](https://github.com/mhvis/solar) | Inverter has Ethernet / WiFi stick on LAN |
| [lucascosti inverter_monitor](https://lucascosti.com/blog/2017/08/logging-solar-inverter-output-with-a-raspberry-pi/) | Classic Perl → PVOutput path |

## Safety

- Mains and PV DC are dangerous. If you are not comfortable opening the inverter or fitting CTs in a consumer unit, hire an electrician.
- Do not defeat anti-islanding or grid-protection settings.
- Isolated RS485 protects the Pi from common-mode noise and ground loops.

## Tests (no hardware)

```bash
cd solar-monitor
python -m unittest discover -s tests -v
```
