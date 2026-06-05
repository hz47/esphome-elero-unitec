#!/usr/bin/env python3
"""
Recover the per-blind encryption seed constant C for a len=27 (UniTec-style) Elero remote.

The transmit payload is scrambled with a counter-derived seed:
        seed = (C - cnt * 0x708f) & 0xffff
where C is constant for a given blind/remote pair. andyboeh's len=29 path uses C=0x0000;
the author's UniTec blind uses C=0x4751. Yours may differ.

HOW TO USE
----------
1. Flash the real component with `logger: level: DEBUG` and press your remote (UP/DOWN/STOP).
2. From the `RAW RX:` lines, grab a few DIRECT packets (where bwd == src == fwd) and read:
     - the counter (the `cnt=` field, in decimal), and
     - the last 8 bytes of the RAW RX line (the encrypted payload).
3. Fill in CAPTURES below and run:  python3 recover_seed_constant.py
4. It prints C. Put that value in elero.cpp (replace 0x4751 in the len=27 send path).
"""

flash_table_decode = [0x0a,0x03,0x01,0x0c,0x0d,0x07,0x0f,0x06,0x00,0x08,0x0b,0x0e,0x09,0x02,0x05,0x04]

def dec_nibbles(m):
    for i in range(8):
        nh, nl = (m[i] >> 4) & 0xF, m[i] & 0xF
        m[i] = ((flash_table_decode[nh] << 4) | flash_table_decode[nl]) & 0xff

def sub_r20(m, r20, start, length):
    for i in range(start, length):
        d = m[i]
        ln = (d - r20) & 0x0F
        hn = ((d & 0xF0) - (r20 & 0xF0)) & 0xFF
        m[i] = hn | ln
        r20 = (r20 - 0x22) & 0xFF

def recover_seed(ciphertext8):
    """Return the raw counter-derived seed (msg[0],msg[1]) hidden in a captured packet."""
    m = list(ciphertext8)
    dec_nibbles(m)
    sub_r20(m, 0xFE, 0, 2)
    return (m[0] << 8) | m[1]

# (counter_decimal, [8 encrypted payload bytes = last 8 bytes of the RAW RX line])
CAPTURES = [
    (230, [0x2f,0x01,0x43,0xf6,0xe8,0x91,0x2f,0x85]),
    (231, [0x0f,0x2f,0x53,0x48,0x38,0x23,0x9f,0xc9]),
    (232, [0x11,0x9e,0xc6,0xd2,0x11,0xb4,0x55,0xbc]),
    (235, [0xbd,0x49,0x8b,0xcf,0x9d,0xe9,0x37,0x43]),
    (238, [0xc8,0xda,0x59,0x35,0x4f,0x8a,0xc8,0x96]),
]

if __name__ == "__main__":
    consts = set()
    for cnt, ct in CAPTURES:
        seed = recover_seed(ct)
        C = (seed + cnt * 0x708f) & 0xffff   # invert: seed = (C - cnt*0x708f) => C = seed + cnt*0x708f
        consts.add(C)
        print(f"cnt={cnt:5d}  recovered_seed=0x{seed:04x}  ->  C=0x{C:04x}")
    print("-" * 40)
    if len(consts) == 1:
        print(f"CONSTANT C = 0x{consts.pop():04x}   (consistent across all captures)")
    else:
        print("Inconsistent C across captures:", [f"0x{c:04x}" for c in consts])
        print("Double-check you used DIRECT packets (bwd == src) and decimal counters.")
