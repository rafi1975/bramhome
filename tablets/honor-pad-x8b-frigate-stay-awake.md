# Honor Pad X8b: keep the screen bright for Frigate CCTV

The Pad X8b is a good wall tablet for a Frigate live view, but MagicOS still dims or sleeps the display after idle time even when **Developer options** are enabled. **Stay awake** only means “do not turn the screen *off* while charging.” It does **not** lock brightness, and it does not override Honor’s sleep timer, adaptive brightness, or power-saving modes.

Goal: wall-powered tablet, Frigate dashboard always visible at a fixed brightness, no dim after ~30 minutes.

---

## Why Developer options are not enough

| Setting | What it actually does |
|---------|------------------------|
| **Developer options → Stay awake** | While plugged in, blocks the final *screen-off*. Brightness can still drop. |
| **Display → Sleep** | How long until MagicOS blanks the panel when nothing is touching it. Often maxes at **10 minutes**; “Never” is missing on many builds. |
| **Adaptive / Automatic brightness** | Light sensor keeps changing brightness; a dark room looks like “random dimming.” |
| **Battery → Power saving** | Lowers brightness and throttles the UI even on charge. |

So “Developer options on” is step one, not the fix. For a CCTV kiosk you need a **wake lock + fixed brightness** (Fully Kiosk is the usual Frigate/Home Assistant choice), plus MagicOS battery exemptions.

The Pad X8b uses an **LCD** (not OLED), so leaving it on 24/7 is fine for burn-in risk. Keep it on a wall charger.

---

## 5-minute MagicOS checklist

Do these once, then pick a viewing method below.

### 1. Display

1. **Settings → Display & brightness**
2. Turn **Automatic** / **Adaptive brightness** **off**
3. Drag brightness to the level you want for the room (leave it there)
4. **Sleep** → longest value, or **Never** if it exists
5. Turn **Eye Comfort** / **Circadian Night Display** / **Natural Tone** **off** (they warm and darken the panel on a schedule)
6. Optional: set refresh rate to **Standard** if you want less heat on a wall mount

### 2. Battery

1. **Settings → Battery** (or **System Manager → Battery**)
2. **Battery usage mode** → **Performance** (or at least not **Power saving**)
3. For the browser / Fully Kiosk / Chrome: **App launch** / **Battery** → **Manage manually** → allow **Auto-launch**, **Secondary launch**, **Run in background** (wording varies by MagicOS version)
4. Disable any “smart power” / “close apps after X minutes of inactivity” for that app

### 3. Developer options (keep these)

1. Unlock if needed: **Settings → About tablet** → tap **Build number** seven times
2. **Developer options → Stay awake** → **on** (screen never sleeps *while charging*)
3. Leave the tablet plugged into a **wall** charger, not a weak USB data port

### 4. Lock screen

For a dedicated CCTV panel:

- **Settings → Lock screen** (or **Biometrics & password**) → swipe / none, or a short PIN you accept entering after power loss
- Turn off **Sleep** lock that re-locks immediately after blanking if you still have a short Sleep value

---

## Recommended: Fully Kiosk Browser + Frigate

Chrome’s Screen Wake Lock can work while the Frigate tab is foreground, but MagicOS OEM policies still dim many tablets. **[Fully Kiosk Browser](https://www.fully-kiosk.com/)** holds a real Android wake lock and can pin brightness.

1. Install Fully Kiosk Browser from Google Play (Plus unlock optional; **Keep Screen On** is in the free tier).
2. Set **Start URL** to your Frigate UI, e.g. `http://frigate.local:5000` or your HTTPS reverse-proxy URL.
3. **Settings → Device Management**:
   - **Keep Screen On** → on  
   - **Screen Brightness** → fixed value (try **180–220**; empty = system default and dims again)  
   - **Screen Off Timer** → off / 0 if present  
   - **Screensaver** → off (or timer **0**) so Fully does not dim on idle
4. **Settings → Web Content Settings**: enable desktop mode if the Frigate live grid looks cramped.
5. **Settings → Kiosk Mode** (optional): pin Fully so back/home cannot leave the cameras.
6. **Settings → Other Settings → Autostart after reboot** → on (and grant MagicOS auto-launch as above).
7. Reboot once while plugged in; confirm brightness stays put for well over 30 minutes.

Home Assistant users can also use the [Fully Kiosk integration](https://www.home-assistant.io/integrations/fully_kiosk/) later to set brightness or wake remotely.

### Frigate in a normal browser

If you stay on Chrome / Firefox:

- Open Frigate over **HTTPS** if possible (Wake Lock needs a secure context; `localhost` and some LAN setups vary).
- Keep the Frigate tab **foreground and unmuted focus** — background tabs release the wake lock.
- Recent Frigate UIs use a screen wake lock while the page is active; that still loses to MagicOS if Sleep / Power saving fight it. Prefer Fully Kiosk on this tablet.

---

## Escalation: ADB (when Sleep has no “Never”)

From a PC with [platform-tools](https://developer.android.com/tools/releases/platform-tools):

1. On the tablet: **Developer options → USB debugging** → on  
2. Plug in USB, accept the RSA prompt  
3. On the PC:

```bash
adb devices
# Stay awake on AC + USB (same as Developer options → Stay awake)
adb shell settings put global stay_on_while_plugged_in 3
# Screen-off timeout ≈ 24.9 days (Android int max)
adb shell settings put system screen_off_timeout 2147483647
# Confirm
adb shell settings get global stay_on_while_plugged_in
adb shell settings get system screen_off_timeout
```

`stay_on_while_plugged_in` values: `0` off, `1` AC only, `2` USB only, `3` AC or USB.

This still does not always stop **brightness** dimming. Pair it with Fully’s fixed **Screen Brightness**, or:

```bash
# Example: fixed brightness ~200/255; disable adaptive
adb shell settings put system screen_brightness_mode 0
adb shell settings put system screen_brightness 200
```

A factory reset or big MagicOS update can wipe these; re-run after updates.

---

## Lightweight alternative: Caffeine

If you do not want Fully Kiosk, a keep-awake app such as **Caffeine** (timeout → infinite / forever) can hold the screen on while Frigate runs in Chrome. Exempt it from MagicOS battery killing the same way. It is a weaker kiosk story (no brightness pin, no autostart kiosk) but enough for a desk tablet.

---

## Quick diagnosis

| Symptom after ~30 min | Likely cause | Fix |
|-----------------------|--------------|-----|
| Screen goes fully black, wakes on tap | Sleep / timeout still active; Stay awake not applied or not charging | Wall charger + Stay awake + Sleep longest/Never or ADB `screen_off_timeout` |
| Screen stays on but much darker | Adaptive brightness, Power saving, Eye Comfort, or no fixed brightness | Manual brightness + Fully **Screen Brightness** + disable Power saving |
| Fine in Fully, dims in Chrome | Wake lock released / OEM ignores browser | Use Fully Kiosk for the wall panel |
| Dim only at night | Circadian / Eye Comfort schedule | Turn those off |
| Dim after reboot | App not auto-started; Stay awake only while charging | Fully autostart + keep plugged in |

---

## Hardware notes (Pad X8b)

- **11″ LCD**, ~1920×1200, MagicOS on Android — good always-on candidate.
- Prefer a **proper USB-C wall charger** (tablet rated charger or quality PD brick). A PC USB port may charge too slowly for Stay awake to stay reliable under load.
- Mount landscape; force orientation in Fully if the Frigate grid rotates after wake.

---

## Sources

- Honor: [Set the screen timeout (Sleep)](https://www.honor.com/uk/support/content/en-us15840786/), [screen too dark / adaptive & power saving](https://consumer.huawei.com/en/support/content/en-us00410352/) (Huawei/Honor shared stack)
- Android kiosk timeout via ADB: `screen_off_timeout` max `2147483647` ms ([emteria notes](https://emteria.com/blog/android-screen-timeout))
- [Fully Kiosk — Keep Screen On / brightness](https://www.fully-kiosk.com/en/)
- [Frigate wake-lock discussion](https://github.com/blakeblackshear/frigate/discussions/4237) (newer UI includes wake lock; OEM tablets still need Fully)
