# A52s STM FTS5CU56A touch replacement design

The bundled SM7325 kernel contains `drivers/input/touchscreen/stmfts.c` and
the Samsung `drivers/input/sec_input/stm/` implementation. The smaller
`stmfts.c` implementation is the protocol reference for the first XNU driver.

## Confirmed controller contract

- Controller: `stm,stm_ts`, FTS5CU56A, address `0x49`.
- Bus: the A52s touchscreen overlay calls it QUPv3 SE8; its live GENI mapping
  is `qcom,i2c-geni@0x00a94000`.
- Event command: `READ_ALL_EVENT` `0x86`, returning up to 32 eight-byte
  records. `READ_ONE_EVENT` is `0x85`; it is diagnostic-only until the GENI
  repeated-start path is validated.
- Commands: `MS_MT_SENSE_ON` `0x93`; `CLEAR_EVENT_STACK` `0xa1`.
- Event low nibbles: detected `0x02`, enter `0x03`, leave `0x04`, motion
  `0x05`. The contact slot is byte 0 high nibble. Coordinates are
  `x = b1 | ((b2 & 0x0f) << 8)` and `y = (b2 >> 4) | (b3 << 4)`.
- The panel reports 4096×4096 coordinates and supports ten contacts. Scale
  before `sweet_hid_touch()` as `x * 1079 / 4095`, `y * 2399 / 4095`.
- The only declared controller GPIO is IRQ GPIO81. The on-state pinctrl is
  input plus bias-disable; its off-state is input plus pull-down. There is no
  reset GPIO in the live A52s node, so GPIO81 must never be driven as reset.
- AVDD is `pm8350c_l7`, whose Yupik regulator node has RPMh resource name
  `ldoc7`, 3.0–3.544 V range and 3.0 V initial HPM setting. The touch node is
  `sec,regulator_boot_on` and `sec,unuse_dvdd_power`: there is no second A71
  PMIC-GPIO DVDD rail to configure.

`tools/stmfts_protocol.py` is the executable host-side decoder reference.

## Replacement patch boundary

The current patch named `0082-sweet-samsung-sec-ts-touch.patch` is not an A52s
driver. It retains the A71/SM7150 SE7 base (`0x00a84000`), GCC clock offsets,
PM6150 GPIO4 writes, GPIO6/7 bit-bang fallback, a GPIO8 reset pulse and the
`sec_ts` name. Its decoder also accepts event `0x02` as a contact and therefore
misses actual enter/move records. Patches 0083 and 0084 further modify that
A71-only path. None may be enabled on A52s.

Patch 0085 adds `bsd/dev/sweet_stmfts.c` after the historical patches and
dispatches to it only with `a52sstmfts=1`. The inherited driver remains
available behind its separate `sweettouch=1` opt-in, but is disabled by
default. The first STM implementation has an intentionally narrow scope:

1. Map only GENI `0x00a94000` and TLMM `0x0f000000`; log GENI firmware/FIFO
   state and GPIO81 level before writing either block.
2. Do not reuse A71 GCC offsets. Enable the three SE clock branches only after
   their Yupik GCC register offsets have been derived from the target GCC
   driver or observed from an ABL-initialized boot. Do not reconfigure the I²C
   SDA/SCL pinmux until the live A52s pin state is recorded.
3. Extend `sweet_rpmh_vreg_enable()` with an explicit `ldoc7`, 3000 mV policy.
   Keep its command-DB lookup and one-transaction safety checks; reject a
   missing/ambiguous `ldoc7` entry.
4. Treat GPIO81 as input only. A rail vote and its bounded settling delay are
   the reset sequence; no fabricated reset GPIO or PMIC GPIO write is allowed.
5. Add a GENI combined write/read transfer for command `0x86` and a 256-byte
   bounded receive path, or demonstrate that 32 `0x85` reads are equivalent on
   the live chip. The inherited 90-byte, single-direction FIFO helper cannot
   read the STM event stack correctly.
6. Decode enter/motion/leave records into a persistent ten-bit contact mask,
   emit one HID frame per stack, and clear the event stack only after an error
   or malformed record. Unknown/status records are logged and ignored.

The protocol fixture covers a full 32-record stack, mixed enter/move/leave
ordering, a no-event terminator, invalid slots, and the maximum 12-bit
coordinates. A 12-bit packed coordinate cannot encode a value above 4095.
The first handset image must omit `a52sstmfts=1`; transport remains opt-in
until the CI image is built and inherited-state diagnostics have been reviewed.
