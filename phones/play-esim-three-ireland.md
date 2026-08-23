# Play eSIM on a Three Ireland iPhone: “eSIM Not Supported”

Scanning a Play Poland QR code on an Irish Three (`three.ie`) iPhone and getting **eSIM Not Supported** (sometimes **This eSIM is from a carrier that is not currently supported on this iPhone**) is almost never a broken QR code. The iPhone is rejecting Play because it is still **locked to Three**.

Apple’s Dual SIM rule is explicit: to use two different carriers at once, the iPhone must be unlocked.

Goal of this setup: keep the Three Ireland nano-SIM for Irish calls/data, and add Play as a second line (eSIM) for the Polish number.

---

## 60-second diagnosis

Do these two checks before asking Play for another QR.

### 1. Carrier lock (the usual cause)

1. Open **Settings → General → About**  
   Polish iOS: **Ustawienia → Ogólne → Informacje**
2. Scroll to **Carrier Lock** / **Network Provider Lock**  
   Polish: **Blokada operatora**
3. Read the value:

| Carrier Lock says | Meaning | Next step |
|-------------------|---------|-----------|
| **No SIM restrictions** / **Brak ograniczeń karty SIM** | Unlocked. Play is allowed. | Skip the unlock section; go to [Install the Play eSIM](#install-the-play-esim) |
| **SIM locked**, **Locked to Three**, or anything else | Locked to Three. Play eSIM will be refused. | Unlock with Three first |

### 2. Does this iPhone even have eSIM hardware?

On the Phone keypad dial **`*#06#`**.

| What you see | Meaning |
|--------------|---------|
| An **EID** number as well as IMEI | eSIM hardware is present (iPhone XS / XR and later, except most mainland-China models) |
| IMEI only, no EID | No eSIM. A Play QR will never install. Use a physical Play nano-SIM, or a different phone |

Mainland-China iPhones (model numbers often ending **CH/A**) use two physical nano-SIMs and typically have **no eSIM**. If **Add eSIM** / **Dodaj eSIM** is missing from Settings, that is the reason — not Three.

Also confirm iOS is current: **Settings → General → Software Update**.

---

## Why Three Ireland phones do this

Phones sold by Three Ireland are locked to the Three network. They will use Three in Ireland, and they will roam abroad on Three’s roaming partners, but they will **not** accept a SIM or eSIM from another operator (Play, Vodafone, a travel eSIM, etc.) until Three unlocks the device.

That lock lives on Apple’s activation servers, tied to the IMEI. Scanning the Play QR again, resetting the iPhone, or buying an “IMEI unlock” website code will not remove it. Only Three can.

---

## Unlock the iPhone with Three first

Do **not** start a Play SIM → eSIM conversion until Carrier Lock already says **No SIM restrictions**. Play will disable the old plastic SIM about **3 hours** after conversion starts. If the iPhone is still locked, the Polish number can go dark with nothing installed to replace it.

### Eligibility (Three Ireland unlocking policy)

Confirm on [Three’s unlocking policy](https://www.three.ie/legal/policies/unlocking-policy.html) — rules can change. Typical current rules:

**Bill Pay**

- Account not suspended / not in collections
- Minimum term finished and you have not upgraded: unlock is free
- Still inside minimum term: Three can require payment of the remaining monthly charges before they unlock

**Prepay (Three Ireland)**

- Handset associated with your Three Ireland account
- At least **€130** genuine top-up on that account (bonus / promo credit does not count)

**Former O2 / Three Ireland Services Hutchison**

- Prepay: associated Three Ireland device, **€150** top-up since association
- Bill Pay: associated, not suspended, no overdue balance

### Request the unlock

1. Get the IMEI: dial **`*#06#`**, or **Settings → General → About → IMEI**.
2. Submit the request at **[three.ie/unlock-my-phone](https://www.three.ie/unlock-my-phone/)** (Three mobile number + IMEI). You should get a verification SMS.
3. If the form fails, use Three Care:
   - From a Three phone in Ireland: **1913**
   - From another network / abroad: **+353 83 333 3333**
   - Chat on [three.ie/contact-us](https://www.three.ie/contact-us.html)

Three’s page talks about an “unlock code”. On **iPhone** you normally **do not type a PIN**. Three tells Apple; Apple updates the lock on the next activation check. Three quote **up to a few working days** (they often say around 2–3).

Skip paid third-party “unlock” sites. Three’s agreement also forbids unofficial unlocking while you are still in contract.

### Confirm the unlock actually landed on the phone

Wait for Three’s confirmation, then:

1. Connect to Wi-Fi, restart the iPhone.
2. Check **Settings → General → About → Carrier Lock** again.
3. It must read **No SIM restrictions**.

If Three says it is unlocked but Carrier Lock has not changed:

1. Keep the Three SIM in, stay on Wi-Fi, restart again.
2. Apple’s fallback: back up, erase the iPhone, restore from that backup ([Apple: unlock iPhone](https://support.apple.com/en-ie/HT201328)). That forces a fresh check with Apple’s servers.
3. If it still shows locked, go back to Three Care — they have not finished the Apple-side unlock.

Do not scan the Play QR until this line is green.

---

## Install the Play eSIM

Use a **second screen or a printout** for the QR. The iPhone camera cannot scan a QR that is on the same iPhone’s display.

Preferred path (more reliable than the Camera app):

1. Join a stable **Wi-Fi** network. Turn VPN off.
2. **Settings → Mobile Service** (or **Cellular** / **Sieć komórkowa**)
3. **Add eSIM** / **Dodaj eSIM** → **Use QR Code** / **Użyj kodu QR**
4. Scan the Play QR.
5. Follow the prompts. Label the new line **Play PL** (and rename Three to **Three IE** if asked).

If the camera will not lock onto the code, tap **Enter Details Manually** / **Wprowadź dane ręcznie** and type the **SM-DP+** address and **activation code** from Play’s email or salon printout. Do not invent an SM-DP+; it is unique to that eSIM.

Play’s iPhone notes: [play.pl/uslugi/esim/apple-iphone](https://www.play.pl/uslugi/esim/apple-iphone)

### If this QR was already scanned once

Play QRs are typically **single-use**. One failed scan on a locked phone often does **not** consume the profile (the download never finished). Still:

- Stop repeatedly scanning the same code.
- After unlock, try **once** from **Settings → Add eSIM**.
- If iOS says the plan is already used, or nothing downloads: ask Play for a **new** QR. Do not buy a second starter until Play confirms the first profile is dead.

Play (from Ireland):

- Play24 app → **Your SIM card** / **Twoja karta SIM** (reissue / finish install)
- From a Play number: **\*500**
- From Three / abroad: **+48 790 500 500**
- Salon Play in Poland with ID (plastic SIM ↔ eSIM swap is free)

### If you converted a plastic Play SIM to eSIM

Play24 / salon conversion: the old nano-SIM stays alive about **3 hours**, then Play switches it off.

- Unlock the iPhone **before** starting conversion.
- If conversion already started and the iPhone was still locked, call Play immediately and say the eSIM would not install (**eSIM Not Supported** / phone locked to Three Ireland). They can issue a new QR or a new plastic SIM.
- Play24 iOS conversion notes: [play.pl/pomoc/aplikacja-play24/karta-sim-esim](https://www.play.pl/pomoc/aplikacja-play24/karta-sim-esim)

---

## Dual SIM settings once Play is on the phone

You are living on Three in Ireland. Play in Ireland is **EU roaming**, not a home network.

**Settings → Mobile Service / Cellular**

| Setting | Recommended in Ireland | Why |
|---------|------------------------|-----|
| **Cellular Data** | **Three IE** | Avoid Play EU fair-use / roaming data while you already have Irish data |
| **Allow Cellular Data Switching** | **Off** | Stops iOS silently using Play for data when Three blips |
| **Default Voice Line** | **Three IE** for Irish contacts, or **Play PL** if most calls are to Poland | You can still pick the other line per call |
| On the **Play PL** line: **Turn On This Line** | On | Polish number rings |
| On the **Play PL** line: **Data Roaming** | **On** | Required for Play to attach in Ireland (calls/SMS). Keep **Cellular Data** on Three so this does not become your internet |
| On the **Three IE** line: **Data Roaming** | Off unless you are leaving Ireland | Avoid Three roaming charges abroad |
| **Wi-Fi Calling** | On for both lines if Three/Play offer it | Incoming calls on the idle line are less likely to dump to voicemail |

iMessage / FaceTime: **Settings → Messages** and **FaceTime** — you can enable both numbers.

When you travel to Poland, flip **Cellular Data** to **Play PL** and turn Three **Data Roaming** off (or turn the Three line off) so Irish roaming does not pay for Polish data.

---

## If it still says eSIM Not Supported after unlock

Work down this list; do not skip.

1. Carrier Lock is **No SIM restrictions** (re-check after a restart).
2. **`*#06#`** shows an **EID**.
3. **Add eSIM** exists in Settings. If it does not, this hardware cannot take Play eSIM.
4. Wi-Fi works (Safari loads). VPN off.
5. Install from **Settings → Add eSIM**, not only the Camera app.
6. One clean scan / one manual SM-DP+ attempt, then stop.
7. New QR from Play if the code is spent.
8. Three Care if Carrier Lock still does not say unlocked.
9. Apple Support only after 1–4 are proven — they cannot unlock a Three phone.

---

## Contacts (official only)

| Who | What | Where |
|-----|------|--------|
| Three Ireland | Unlock request | [three.ie/unlock-my-phone](https://www.three.ie/unlock-my-phone/) |
| Three Ireland | Unlock rules | [Unlocking policy](https://www.three.ie/legal/policies/unlocking-policy.html) |
| Three Care | Form / lock stuck | 1913 or +353 83 333 3333 — [contact](https://www.three.ie/contact-us.html) |
| Apple | What “unlocked” means | [support.apple.com/en-ie/HT201328](https://support.apple.com/en-ie/HT201328) |
| Apple | Dual SIM | [Use Dual SIM on iPhone](https://support.apple.com/en-ie/guide/iphone/iph9c5776d3c/ios) |
| Play | iPhone eSIM | [play.pl/uslugi/esim/apple-iphone](https://www.play.pl/uslugi/esim/apple-iphone) |
| Play | Play24 SIM → eSIM | [Karta SIM/eSIM](https://www.play.pl/pomoc/aplikacja-play24/karta-sim-esim) |
| Play Care | New QR / dead plastic SIM | \*500 or +48 790 500 500 |

Do not factory-reset as a first fix. It will not unlock the phone, and it can delete an eSIM that *did* install.
