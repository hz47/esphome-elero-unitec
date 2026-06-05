# Diagnostic toolkit

These are standalone ESPHome configs that talk to the CC1101 **directly** with raw register
commands — no Elero component involved. That's the point: they isolate *hardware* problems
from *software* problems during bring‑up. Flash one, open the ESPHome logs, and read.

All of them use the same wiring as the main config (software SPI on GPIO18/23/19, CS GPIO4).

| File | What it answers | What to look for |
|---|---|---|
| `01-cc1101-selftest.yaml` | Is the chip alive and is SPI wired correctly (both directions)? | `VERSION=0x14` (or `0x04`/`0x07` on clones) + `readback=0x2D` → **alive**. `VERSION=0x00`/`0xFF` → MISO/SPI/power problem. |
| `02-rssi-peak-meter.yaml` | Does the antenna/receiver hear the remote *at all*? Samples continuously so it can't miss a burst. | Hold the remote on the board: `PEAK=-30…-65 dBm  SIGNAL DETECTED` → antenna OK. Stays `~-90` → antenna not soldered / dead RF path. |
| `03-freq0-finder.yaml` | **The key tool.** What `freq0` does your module actually decode at? | Hold the remote ~40 s: `*** FOUND! FREQ0=0xXX  src=0x…` → put `0xXX` in your config's `freq0`. |
| `04-freq-wide-finder.yaml` | If `freq0` alone finds nothing — sweeps `freq1` (bigger steps) and shows peak RSSI + frequency error per step. | Line with strongest `peakRSSI` / `SIGNAL HERE` / `DECODED` tells you the right `freq1`. |
| `05-rssi-freqest-meter.yaml` | Fine frequency error (FREQEST) while a strong signal is present. | `FREQEST=±N (±N kHz)` when RSSI is high → how far off you are. |
| `06-gdo0-test.yaml` | Is the GDO0 pin wired/working? (Only relevant if you want the interrupt path; this fork polls instead.) | Toggles logged on remote activity. |

## Recommended order

```
01  →  02  →  03   (→ 04 only if 03 finds nothing)
```

Once `03` (or `04`) gives you a frequency where packets decode, put it in your main config,
flash the real component, and you're receiving. Everything else follows from there.

> Tip: hold the remote button **down** during the sweeps so it keeps transmitting through
> the whole scan, and keep it physically on top of the module.
