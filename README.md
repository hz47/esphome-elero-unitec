# esphome-elero-unitec

Control **Elero** roller blinds (Rolladen) from **Home Assistant** with an **ESP32 + CC1101**
868 MHz module running **ESPHome**. Works with **Elero UniTec‑868** remotes (the short `len=27`
packet variant).

Fork of [andyboeh/esphome-elero](https://github.com/andyboeh/esphome-elero) with two fixes for
cheap CC1101 clones + UniTec remotes:

- **Per‑module frequency calibration** — clone crystals are off enough that the stock `freq0`
  *hears* the remote but never *decodes* it. A sweep tool finds the right value.
- **Counter‑derived encryption seed** (`len=27`) — `seed = (C − cnt·0x708f) & 0xffff`, so
  transmitted packets match the real remote byte‑for‑byte.

> Hobby fork of an early‑stage component — expect some bring‑up work.

## How it works

Elero is a **bidirectional, rolling‑code** 868 MHz protocol. You can't pair a new remote — the
component **impersonates one you already own**: it receives your remote to learn its identity,
then transmits look‑alike packets, keeping the rolling counter one step ahead (auto‑synced
whenever it hears the real remote).

## Hardware

Any **ESP32** + a **CC1101 868 MHz** module (green clones are fine). Uses software SPI; GDO0 is
polled, not used as an interrupt.

| CC1101 | ESP32 |
|---|---|
| VCC | 3V3 (3.3 V only) |
| GND | GND |
| SCK | GPIO18 |
| MOSI | GPIO23 |
| MISO | GPIO19 |
| CSN | GPIO4 |
| GDO0 | GPIO26 |
| ANT | coil antenna — **must be soldered on** |

## Setup

**1. Install** — copy `components/elero/` into your ESPHome config folder and reference it:

```yaml
external_components:
  - source: { type: local, path: components }
```

**2. Bring‑up** — flash these in order and watch the logs. They talk to the chip directly, so
they separate hardware faults from software ones:

| Tool | Confirms |
|---|---|
| `tools/01-cc1101-selftest.yaml` | chip + SPI alive |
| `tools/02-rssi-peak-meter.yaml` | antenna hears the remote |
| `tools/03-freq0-finder.yaml` | **your `freq0`** (clone offset) — put it in your config |

(If `03` finds nothing, `tools/04-freq-wide-finder.yaml` sweeps wider. See
[`tools/README.md`](tools/README.md).)

**3. Read your blind's values** — flash [`example.yaml`](example.yaml) with
`logger: level: DEBUG`, press your remote, and read the `rcv'd:` line (use the one where
`src == bwd == fwd`):

| Config key | Log field |
|---|---|
| `remote_address` | `src` |
| `blind_address` | `dst` |
| `channel` | `chl` |
| `pck_inf1` / `pck_inf2` | `typ` / `typ2` |
| `hop` | `hop` |
| `payload_1` / `payload_2` | payload[0] / payload[1] |
| `command_up` / `stop` / `down` | 5th payload byte on UP / STOP / DOWN |

Fill them into `example.yaml`, switch to `logger: level: INFO`, flash — the `Rolladen` cover
appears in Home Assistant.

## Multiple blinds

One ESP/CC1101 drives many blinds — add a `cover:` per blind with its own
`blind_address` / `channel` / `remote_address`. Separate remotes never clash (counters are
tracked per remote). Each cover takes a `seed_constant:` (default `0x4751`); if a blind
receives fine but ignores transmits, recover its constant with
[`tools/recover_seed_constant.py`](tools/recover_seed_constant.py) — see
[`docs/finding-the-seed-constant.md`](docs/finding-the-seed-constant.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| In RX, hears energy, decodes nothing | Frequency offset → run `tools/03-freq0-finder.yaml` |
| `VERSION=0x00` in self‑test | SPI / MISO wiring |
| RSSI never jumps on a remote press | Antenna not soldered to ANT |
| Receives but blind ignores transmits | Wrong `seed_constant` → recover it |
| Physical remote stops working | Press it a few times to resync the rolling code |

Use `logger: level: INFO` for daily use; `DEBUG` adds raw RX/TX for bring‑up.

## License

GPLv3 (derivative of GPLv3 work) — see [LICENSE](LICENSE) and [CREDITS.md](CREDITS.md).
Thanks to **andyboeh**, **stanleypa**, and **QuadCorei8085**.
