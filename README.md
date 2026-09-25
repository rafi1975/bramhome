# Homey Energy Dongle for Home Assistant

The [Homey Energy Dongle](https://homey.app/en-nl/homey-energy-dongle/) is an ESP32-C6 that reads a smart meter's P1 / HAN port. This config replaces the Homey firmware with [ESPHome](https://esphome.io/) so Home Assistant gets the readings directly on your network.

After flashing, the dongle no longer talks to Homey. The original firmware can be restored from [usb.homey.app](https://usb.homey.app).

## What Home Assistant receives

| Entity | Use |
| --- | --- |
| Energy imported | Grid consumption on the Energy dashboard (tariff 1 + tariff 2, or the meter's total register) |
| Energy exported | Energy returned to the grid |
| Power imported / Power exported | Live load, in kW |
| Voltage and current, L1–L3 | Per-phase detail when the meter sends it |
| Gas consumed | Dutch (`0-1:24.2.1`) or Belgian gas register |
| Water consumed | When a water meter is on the P1 bus |
| Peak demand | Belgian quarter-hour peak, when present |
| Status LED | Blue while waiting for a telegram, green after one is parsed |

Registers the meter does not send stay `unavailable`. That is normal for a single-phase meter, or a meter without gas.

## What you need

- Home Assistant with the ESPHome Device Builder add-on **2026.1.0 or newer**. Older releases cannot run the DSMR parser on the ESP32-C6. The add-on compiles this config. The website cannot.
- Chrome or Edge on the computer you will plug the dongle into. The USB flash itself is [ESPHome Web](https://web.esphome.io).
- A USB-C cable that carries data, not charge-only.
- A SIM eject tool or paperclip for the boot button next to the USB-C port.
- The meter's P1 port enabled. Some utilities ship it switched off; power on the port does not mean data is enabled.

## Install

There are two tools, and both are required the first time:

| Tool | Where it is | What it does |
| --- | --- | --- |
| ESPHome Device Builder | Home Assistant → **Settings → Apps** (older installs: **Settings → Add-ons**) | Builds this dongle's firmware from the YAML |
| [web.esphome.io](https://web.esphome.io) | Chrome or Edge on your computer | Writes that firmware to the dongle over USB |

The builder is not under **Settings → Devices & services**. That ESPHome entry only connects to a dongle that is already flashed, and it asks for a host and port.

**Prepare for first use** on the website only installs a blank ESPHome image and can join Wi-Fi. It does not read the meter. Use the steps below to install this config.

1. In Home Assistant, go to **Settings → Apps → Install App** (or **Settings → Add-ons → Add-on Store**). Search for **ESPHome Device Builder**, then click **Install**, **Start**, and **Open Web UI**. If it is missing from the list, open the ⋮ menu, choose **Repositories**, add `https://github.com/esphome/home-assistant-addon`, and search again. If **Apps** and **Add-ons** are both missing, this Home Assistant install cannot run apps; use the [ESPHome Device Builder desktop app](https://esphome.io/install/) instead.
2. On the page that says **Add new device**, click that button, then **Continue**, then **New Device Setup**. Name it `homey-energy-dongle`. Choose **ESP32**, then **ESP32-C6**. Enter your Wi-Fi name and password if it asks. When it says the configuration was created and offers to install, click **Skip**.
3. Click **Edit** on the new device. In the generated text, copy the `key:` value under `api:`. You will need it as `api_encryption_key`. Then select all of the generated text and replace it with [`esphome/homey-energy-dongle.yaml`](esphome/homey-energy-dongle.yaml). Click **Save**.
4. If Save says a secret is missing, open **Secrets** in the Device Builder and add the keys from [`esphome/secrets.yaml.example`](esphome/secrets.yaml.example). The setup wizard usually creates `wifi_ssid` and `wifi_password` already. For `api_encryption_key`, paste the key you copied, or generate one with:

   ```bash
   openssl rand -base64 32
   ```

5. In the Device Builder, click **Install**, then **Manual download**, and choose **Factory format**. Save the `.bin` file. Compiling takes several minutes.
6. On your computer, open [web.esphome.io](https://web.esphome.io) in Chrome or Edge.
7. Put the dongle in flash mode: with it unplugged, hold the button next to the USB-C port, then plug the cable into the computer. The LED stays off in this mode.
8. On the website, click **Connect**, choose the dongle's serial port, click **Install**, and select the factory `.bin` from step 5.
9. When the site says the install succeeded, unplug USB, plug the dongle into the meter, and wait for the LED to turn green.

Home Assistant should discover it under **Settings → Devices & services → ESPHome**. Enter the API encryption key from `secrets.yaml` when asked.

You do not add the DSMR Smart Meter integration. The dongle is already an ESPHome device.

If you already clicked **Prepare for first use** and the dongle joined your Wi-Fi, skip the website install. Paste this YAML into the Device Builder and choose **Wirelessly** when you click Install. Later updates use the network the same way.

## Energy dashboard

**Settings → Dashboards → Energy**

- Grid consumption: **Energy imported**
- Return to grid: **Energy exported**
- Gas: **Gas consumed**

Use the tariff entities (`Energy imported tariff 1` and `tariff 2`) only if you want them split. **Energy imported** is already the sum.

## If the LED stays blue

The firmware is running and no valid telegram has been parsed.

1. Confirm the utility has activated the P1 / HAN port.
2. In the ESPHome logs, look for `telegram` or CRC errors. If you see a stream of bytes and no telegram, set `inverted: false` on GPIO4 and install again.
3. For a DSMR 2.2 meter, use the commented 9600 7E1 UART block and set `crc_check: false`.
4. For an encrypted meter (Luxembourg Smarty), set `decryption_key` from the 32-character key your utility gave you.
5. A Belgian water meter on M-Bus channel 1 needs `water_mbus_id: 1` under `dsmr:`.

## Pins

| Pin | Function |
| --- | --- |
| GPIO4 | P1 receive, inverted |
| GPIO23 | P1 receiver enable, held high |
| GPIO2 | WS2812 LED, color order GRB |

These are the pins published by Athom for this dongle. GPIO23 is turned on at boot; if it stays low the receiver is muted.

## Restore Homey firmware

1. Boot the dongle with the button held, the same way as the first flash.
2. Open [usb.homey.app](https://usb.homey.app) in Chrome or Edge and restore the factory firmware.

Do that before returning or reselling the dongle.
