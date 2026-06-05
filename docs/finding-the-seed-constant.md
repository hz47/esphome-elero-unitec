# Finding your encryption seed constant

> Only needed for **`len=27` (UniTec‑style) remotes**, and only if **reception works but the
> blind ignores your transmits**. If `pck_inf1 > 0x60` (a `len=29` TempoTel remote), this
> doesn't apply.

## Why

Elero scrambles the transmit payload with a seed that changes every counter:

```
seed = (C − cnt · 0x708f) & 0xffff
```

`C` is a constant for a given blind/remote pair. The original `len=29` path uses `C = 0x0000`.
The author's UniTec blind uses **`C = 0x4751`** (the default in `elero.cpp`). Yours may differ —
if so, your transmits will be perfectly formed but scrambled wrong, and the blind will reject
them even though everything else is correct.

## How to recover it (5 minutes)

1. Flash the real component with `logger: level: DEBUG`.
2. Press your physical remote a few times. Capture several `RAW RX:` lines that are **direct**
   transmissions — the ones where `bwd == src == fwd` (no mesh relay). Note for each:
   * the `cnt=` value (decimal), and
   * the **last 8 bytes** of the `RAW RX:` line (the encrypted payload).
3. Open [`../tools/recover_seed_constant.py`](../tools/recover_seed_constant.py), replace the
   `CAPTURES` list with yours, and run:

   ```bash
   python3 tools/recover_seed_constant.py
   ```

   It decrypts the hidden seed from each packet and prints the constant. If your captures are
   good, every line yields the **same** `C`:

   ```
   CONSTANT C = 0x4751   (consistent across all captures)
   ```

4. Put that value into `components/elero/elero.cpp`, in the `len=27` branch of
   `send_command()`:

   ```cpp
   uint16_t code27 = (0x4751 - (cmd->counter * 0x708f)) & 0xffff;   // <- your C here
   ```

5. Recompile, flash, and your transmits will now be byte‑identical to the real remote's.

## Verifying before you flash

The same script can be extended to **re‑encode** a known plaintext and confirm it reproduces
the captured ciphertext exactly — that's how this was validated offline before ever touching
the firmware. Decode is deterministic, so once `C` is right, `encode(plaintext)` equals the
remote's real bytes on every meaningful byte (the final parity byte "doesn't matter" and may
differ).
