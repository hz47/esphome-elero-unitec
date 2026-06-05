# Credits & Attribution

This project stands entirely on the shoulders of others. It is a fork/derivative
of existing work, with two additions that made it work for an **Elero UniTec‑868**
remote driving Elero blinds through a cheap CC1101 clone module:

1. A **per‑module frequency calibration** step (the CC1101 clone's crystal is far
   enough off that the default `freq0` never decodes).
2. The **counter‑derived encryption seed** for the short (`len=27`) packet variant
   that the UniTec remote uses (`seed = (0x4751 − cnt·0x708f) & 0xffff`).

## Upstream projects

| Project | Author | License | What we use |
|---|---|---|---|
| [esphome-elero](https://github.com/andyboeh/esphome-elero) | andyboeh | GPLv3 | The ESPHome component this forks |
| [eleropy](https://github.com/stanleypa/eleropy) | stanleypa | GPLv3 | Remote/packet handling logic |
| [elero_protocol](https://github.com/QuadCorei8085/elero_protocol) | QuadCorei8085 | MIT | Encryption / decryption tables |

Because `eleropy` and `esphome-elero` are GPLv3, this derivative is **GPLv3** too.

## Thanks

To andyboeh especially — the original component's troubleshooting note
("your frequency might have an offset… I had to set my module to `0xc0`")
was the clue that cracked the reception problem.
