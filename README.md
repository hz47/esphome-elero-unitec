# esphome-elero-unitec

Control **Elero** roller blinds (Rolladen) from **Home Assistant** with a cheap **ESP32 + CC1101**
868 MHz radio running **ESPHome**. Made for **Elero UniTec‑868** remotes.

It works by **pretending to be a remote you already own**. Elero uses a two‑way, rolling‑code
signal, so you can't just add a new remote — instead the ESP32 listens to your real remote,
learns its identity, and then sends matching signals (always keeping the rolling code one step
ahead).

This is a fork of [andyboeh/esphome-elero](https://github.com/andyboeh/esphome-elero) with two
fixes needed for cheap CC1101 clones and UniTec remotes:

- **Frequency calibration** — clone radios are slightly off‑frequency: they *hear* the remote
  but can't *decode* it. A small tool finds the correct setting for your board.
- **Correct encryption** — UniTec signals are scrambled with a code that changes on every press.
  This fork reproduces it exactly, so the blind accepts the commands.

> A hobby fork of an early‑stage project — expect a little setup work.

## Hardware

You need an **ESP32** board, a **CC1101 868 MHz** module (cheap green clones are fine), some
jumper wires, and a soldering iron for the antenna.

Wire the CC1101 to the ESP32 like this:

```
  CC1101                 ESP32
  ──────                 ─────
  VCC  ───────────────►  3V3        ⚠  3.3 V only — never 5 V
  GND  ───────────────►  GND
  SCK  ───────────────►  GPIO18
  MOSI ───────────────►  GPIO23
  MISO ───────────────►  GPIO19
  CSN  ───────────────►  GPIO4
  GDO0 ───────────────►  GPIO26
  ANT  ── solder the coil antenna here
```

A few things that matter:

- **Solder the antenna** to the ANT pad — without it the radio is nearly deaf.
- If reception is flaky, **re‑check the MISO wire** first — a loose one looks exactly like a
  software bug.
- Pins are configurable in YAML; these are just the defaults.

## Setup

**1. Install** — copy `components/elero/` into your ESPHome config folder and reference it:

```yaml
external_components:
  - source: { type: local, path: components }
```

**2. Bring‑up** — flash these in order and watch the logs. They talk to the radio directly, so
they tell hardware problems apart from software ones:

| Tool | What it confirms |
|---|---|
| `tools/01-cc1101-selftest.yaml` | the chip is alive and wired right |
| `tools/02-rssi-peak-meter.yaml` | the antenna actually hears your remote |
| `tools/03-freq0-finder.yaml` | **your `freq0` value** — put it in your config |

(If `03` finds nothing, `tools/04-freq-wide-finder.yaml` searches a wider range. Details in
[`tools/README.md`](tools/README.md).)

**3. Read your blind's values** — flash [`example.yaml`](example.yaml) with
`logger: level: DEBUG`, press your remote, and read the `rcv'd:` line (pick the one where
`src == bwd == fwd`):

| Config key | Comes from |
|---|---|
| `remote_address` | `src` |
| `blind_address` | `dst` |
| `channel` | `chl` |
| `pck_inf1` / `pck_inf2` | `typ` / `typ2` |
| `hop` | `hop` |
| `payload_1` / `payload_2` | payload[0] / payload[1] |
| `command_up` / `stop` / `down` | the 5th payload byte when you press UP / STOP / DOWN |

Put them in `example.yaml`, switch to `logger: level: INFO`, and flash — the `Rolladen` cover
shows up in Home Assistant.

## Multiple blinds

One ESP + radio can drive many blinds. Add a `cover:` entry per blind with its own
`blind_address` / `channel` / `remote_address`. Separate remotes never clash (each one's rolling
code is tracked on its own).

Each cover also has a `seed_constant:` (default `0x4751`). If a blind *receives* fine but
*ignores* commands, it uses a different code — recover it with
[`tools/recover_seed_constant.py`](tools/recover_seed_constant.py)
([guide](docs/finding-the-seed-constant.md)).

## Troubleshooting

| Problem | Fix |
|---|---|
| Radio is listening but never decodes anything | Wrong frequency → run `tools/03-freq0-finder.yaml` |
| `VERSION=0x00` in the self‑test | Check the SPI wiring, especially MISO |
| Signal never jumps when you press the remote | Antenna isn't soldered to ANT |
| Receives fine but the blind won't move | Wrong `seed_constant` → recover it |
| Your physical remote stops working | Press it a few times to resync |

Use `logger: level: INFO` for everyday use; `DEBUG` adds the raw radio logs for setup.

## License

GPLv3 (it builds on GPLv3 projects) — see [LICENSE](LICENSE) and [CREDITS.md](CREDITS.md).
Thanks to **andyboeh**, **stanleypa**, and **QuadCorei8085**.
