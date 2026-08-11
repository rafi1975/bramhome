# bramhome

Home automation notes and tools.

## SolarRiver 4400TL

See [`solar-monitor/`](solar-monitor/) for a Raspberry Pi 3 RS485 logger that:

- reads live production stats from a Samil Power SolarRiver 4400TL
- stores history in SQLite
- optionally publishes to MQTT (Home Assistant discovery) and PVOutput
- combines with a grid CT meter to show when solar is covering house load vs importing from the grid

The 4400TL is **grid-tied** — it injects solar in parallel with the grid rather than switching the house off-grid. Details and wiring are in the solar-monitor README.
