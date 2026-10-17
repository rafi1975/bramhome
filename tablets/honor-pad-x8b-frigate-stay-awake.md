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

## Viewing options (pick one)

| Option | Use when | Stay-awake strength |
|--------|----------|---------------------|
| **A. Fully Kiosk + plain HTTP Frigate** | LAN-only tablet; avoid SSL white screens | Best (wake lock + fixed brightness) |
| **B. Fully Kiosk + HTTPS** | You need TLS; fix SSL settings first | Best once SSL stops failing |
| **C. Chrome + Caffeine** | Fully previously white-screened on SSL and you want a simple bypass | Good enough with MagicOS checklist |

---

## A / B — Fully Kiosk Browser + Frigate

Chrome’s Screen Wake Lock can work while the Frigate tab is foreground, but MagicOS OEM policies still dim many tablets. **[Fully Kiosk Browser](https://www.fully-kiosk.com/)** holds a real Android wake lock and can pin brightness.

### How to open Fully’s settings (Honor gesture nav)

On the Pad X8b, **swipe from the left edge is Android’s Back gesture**, so a quick swipe often leaves the page or closes Fully instead of opening Fully’s menu. Fully’s own docs: with gesture navigation you must **hold briefly on the left edge, then swipe right**.

1. Put a finger on the **far left edge** of the screen (bezel / very edge, not mid-page).
2. **Hold still ~0.5–1 second** (you should feel a slight pause; do not flick).
3. Then **drag slowly toward the center**. Fully’s sidebar should appear.
4. Tap **Settings**.

If that still backs out of the app:

| Try this | What it does |
|----------|----------------|
| **Three-button navigation** temporarily | **Android Settings → System & updates → System navigation → Buttons**. Open Fully, swipe left→right for the menu (no hold needed), change Fully settings, switch gestures back later if you want. |
| **Kiosk Mode exit gesture** | If Kiosk Mode (PLUS) is on, left-swipe may only show a **PIN** dialog, not Settings. Enter your Kiosk PIN → then **Settings**, or choose **Disable Kiosk Mode** first. Default exit gesture is often left-swipe; you can change it to **Fast 5 taps** in Kiosk Mode settings once you get in. |
| **Force-stop and relaunch** | **Android Settings → Apps → Fully Kiosk Browser → Force stop**, open Fully again. On first run, tap through until you see **Start Using Fully**, then use hold-then-swipe before enabling Kiosk Mode. |
| **Remote Admin** (if already enabled) | From a PC on the same Wi‑Fi open `http://TABLET_IP:2323` (default), log in, change Start URL / Ignore SSL / brightness without touching the tablet. |

Do **not** enable Kiosk Mode until Stay awake, Start URL, Ignore SSL Errors, and brightness are set — lockdown makes recovering from a white screen harder.

### Avoid the white-screen SSL error (common on this setup)

Fully’s Android WebView often shows a **blank/white page** (sometimes with a brief SSL / `NET::ERR_CERT_*` toast) when the Start URL is **HTTPS with a self-signed, expired, or hostname-mismatched cert** — typical for a home reverse proxy in front of Frigate. Chrome may have let you tap “Advanced → Proceed”; Fully does not show that interstitial by default, so you only see white.

**Preferred on a wall tablet that never leaves the LAN:** point Fully at Frigate’s **HTTP** UI and skip TLS on that path.

1. Start URL examples that avoid SSL entirely:
   - `http://192.168.x.x:5000` (Frigate default UI port)
   - `http://frigate.local:5000` if mDNS resolves on the tablet
2. Do **not** use `https://…` unless the cert is publicly trusted (Let’s Encrypt / real CA) **or** you enable Ignore SSL Errors below.
3. If Frigate is only exposed via an HTTPS proxy (Nginx Proxy Manager, Traefik, Caddy, HA ingress):
   - either add a second **HTTP** listener for the tablet’s IP only, or
   - use Fully’s Ignore SSL Errors (LAN trust trade-off).

**If you must use HTTPS in Fully:**

1. Swipe from the left edge → **Settings → Advanced Web Settings**
2. Enable **Ignore SSL Errors** (lets WebView load self-signed / bad-hostname certs; only safe on a trusted home LAN)
3. Still white? Also try **Graphics Acceleration Mode → Software** (known Fully white-screen workaround on older/odd GPUs)
4. Clear a stuck bad SSL decision:
   - Exit Fully (sidebar → Exit)
   - **Android Settings → Apps → Fully Kiosk Browser → Storage → Clear cache** (Clear data only if you accept re-entering settings)
   - Reopen Fully, confirm Ignore SSL Errors is still on, load the Start URL again
5. Optional: **Web Auto Reload → Auto Reload after Page Error** so a transient cert/proxy blip recovers without a white forever-page

### Fully stay-awake settings

1. Install Fully Kiosk Browser from Google Play (Plus unlock optional; **Keep Screen On** is in the free tier).
2. Set **Start URL** as in the SSL section above (`http://…:5000` preferred).
3. **Settings → Device Management**:
   - **Keep Screen On** → on  
   - **Screen Brightness** → fixed value (try **180–220**; empty = system default and dims again)  
   - **Screen Off Timer** → off / 0 if present  
   - **Screensaver** → off (or timer **0**) so Fully does not dim on idle
4. **Settings → Web Zoom and Scaling** (fixes big gaps vs Chrome — see below).
5. **Settings → Kiosk Mode** (optional): pin Fully so back/home cannot leave the cameras.
6. **Settings → Other Settings → Autostart after reboot** → on (and grant MagicOS auto-launch as above).
7. Reboot once while plugged in; confirm the live view loads (not white) and brightness stays put for well over 30 minutes.

### Camera grid has big gaps (looks fine in Chrome)

Fully uses **Android WebView**, not Chrome. Frigate saves the live-grid layout in **that browser’s local storage**, so Chrome’s tidy layout does not carry over. WebView also often reports a **mobile** viewport, which changes how the default camera dashboard packs tiles and leaves empty black columns.

In Fully, open Settings (hold left edge → swipe):

1. **Web Zoom and Scaling**
   - **View in Desktop Mode** → **on**
   - **Use Wide Viewport** → **on**
   - **Load in Overview Mode** → **off**
   - **Initial Scale** → leave default / empty first; if still sparse try **90** or **80**
2. **Advanced Web Settings → User Agent** (wording: Fake / Custom User Agent) → set a **desktop Chrome** string, e.g.  
   `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
3. Reload the Start URL (sidebar → reload / tap Start URL).

Then **fix the layout inside Fully** (not in Chrome):

1. In Frigate, open a **Camera group** (not only the default “all cameras” dashboard — groups are manually editable).
2. Tap the **layout / edit** control (pencil or grid icon on the live view).
3. Drag and resize the camera tiles to fill the Pad X8b screen; exit edit to save.
4. That layout is stored only in Fully’s WebView. Chrome keeps its own copy.

If the grid is still a mess from an old bad viewport:

- Fully → **Other Settings** → clear **cache / web storage** for the site (or Android **Apps → Fully → Storage → Clear cache**), reload, enable Desktop Mode again, then re-edit the camera group once.

Optional cleaner Start URL for a wall panel:  
`http://192.168.x.x:5000` → open your camera group once and bookmark that path as Start URL so you land on the fixed grid.

Home Assistant users can also use the [Fully Kiosk integration](https://www.home-assistant.io/integrations/fully_kiosk/) later to set brightness or wake remotely. For that integration’s own TLS to Fully’s remote admin, turn **Verify SSL certificate** off if Fully’s remote admin uses a self-signed cert — that is separate from the Start URL SSL issue.

---

## C — Chrome + Caffeine (skip Fully SSL)

If Fully already burned you with a white SSL page and you do not want Ignore SSL Errors:

1. Install **Caffeine** (or similar keep-awake) → set timeout to **infinite / forever**; exempt it from MagicOS battery kill (same as the Battery checklist).
2. Open Frigate in **Chrome**:
   - Prefer `http://192.168.x.x:5000` on LAN (no cert fight).
   - If you use HTTPS, tap through the cert warning once in Chrome (Chrome keeps that exception; Fully did not).
3. Keep the Frigate tab **foreground**. Background tabs drop wake locks; Caffeine covers the OS sleep side.
4. Still apply the MagicOS Display + Battery checklist so adaptive brightness / Power saving do not dim the panel under Chrome.

Recent Frigate UIs also request a Screen Wake Lock while the page is active; on Honor tablets that alone is often not enough — keep Caffeine (or Fully) in the loop.

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

## Quick diagnosis

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Left-edge swipe **exits Fully** / goes Back instead of Settings | MagicOS gesture navigation steals the swipe | **Hold ~1s on left edge, then swipe**; or switch to **3-button nav** temporarily |
| Left-edge swipe asks for a **PIN** | Kiosk Mode is on; that swipe is the exit gesture | Enter Kiosk PIN → Settings (or disable Kiosk Mode) |
| Fully opens to **white screen** / SSL error | HTTPS self-signed or bad hostname; WebView blocks without interstitial | Use `http://IP:5000`, or **Ignore SSL Errors** + clear Fully cache |
| White screen even on HTTP | WebView / GPU glitch | **Graphics Acceleration → Software**; auto-reload after page error |
| Camera grid has **big black gaps**; Chrome looks fine | Fully WebView = mobile viewport + separate Frigate layout storage | **View in Desktop Mode** + desktop User Agent; edit camera-group layout *inside Fully* |
| Screen goes fully black after ~30 min, wakes on tap | Sleep / timeout still active; Stay awake not applied or not charging | Wall charger + Stay awake + Sleep longest/Never or ADB `screen_off_timeout` |
| Screen stays on but much darker | Adaptive brightness, Power saving, Eye Comfort, or no fixed brightness | Manual brightness + Fully **Screen Brightness** + disable Power saving |
| Fine in Fully, dims in Chrome | Wake lock released / OEM ignores browser | Fully Kiosk, or Chrome + Caffeine |
| Dim only at night | Circadian / Eye Comfort schedule | Turn those off |
| Dim after reboot | App not auto-started; Stay awake only while charging | Fully/Caffeine autostart + keep plugged in |

---

## Hardware notes (Pad X8b)

- **11″ LCD**, ~1920×1200, MagicOS on Android — good always-on candidate.
- Prefer a **proper USB-C wall charger** (tablet rated charger or quality PD brick). A PC USB port may charge too slowly for Stay awake to stay reliable under load.
- Mount landscape; force orientation in Fully if the Frigate grid rotates after wake.

---

## Sources

- Honor: [Set the screen timeout (Sleep)](https://www.honor.com/uk/support/content/en-us15840786/), [screen too dark / adaptive & power saving](https://consumer.huawei.com/en/support/content/en-us00410352/) (Huawei/Honor shared stack)
- Android kiosk timeout via ADB: `screen_off_timeout` max `2147483647` ms ([emteria notes](https://emteria.com/blog/android-screen-timeout))
- [Fully Kiosk — Keep Screen On / Ignore SSL Errors / brightness](https://www.fully-kiosk.com/en/)
- Fully white screen: [HA community — Graphics Acceleration → Software](https://community.home-assistant.io/t/the-nightmare-of-fully-kiosk-browser-white-screen/592959)
- [Frigate wake-lock discussion](https://github.com/blakeblackshear/frigate/discussions/4237) (newer UI includes wake lock; OEM tablets still need Fully or Caffeine)
