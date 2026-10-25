# Galaxy A52s live hardware evidence

Source: root ADB on model `SM-A528B`, plus `a52s-live.dtb` captured on
2026-10-23. The DTB and device dumps are local-only artifacts and are not
committed.

Confirmed (the values below are the profile source for this port):

- SoC: SM7325 / Snapdragon 778G, eight Kryo 670 cores. Captured CPU IDs are
  CPUs 0-3 Cortex-A55 (`MIDR.part 0xd05`) and CPUs 4-7 Cortex-A78 (`0xd41`).
- GICD `0x17a00000` (64 KiB), GICR `0x17a60000` (1 MiB); timer blocks
  `0x17c20000` and `0x17c21000`, CNTFRQ 19.2 MHz;
- UFS host `0x01d84000`, IRQ 297, boot device `1d84000.ufshc`; UFS PHY
  `0x01d87000`; UFS ICE `0x01d88000`;
- MDSS `0x0ae00000`;
- QUPv3 SE8 I²C `0x00a94000`, `qcom,i2c-geni`;
- touchscreen `stm,stm_ts` / FTS5CU56A at I²C address `0x49`; IRQ GPIO 81,
  level-triggered; AVDD PM8350C LDO7 (`pm8350c_l7` / `ldoc7`); no reset GPIO
  is declared; touchscreen dimensions `0x1000 × 0x1000`;
- firmware: `tsp_stm/fts5cu56a_a52sxq.bin`;
- USB DWC3 `0x0a600000`;
- live-DT splash region: `0xe1000000`, size `0x02300000`.
- DRM reports the primary panel modes `1080x2400x120x184672cmdHS` and
  `1080x2400x60x184672cmdHS`.

The live `/proc/iomem` confirms the framebuffer reservation as
`0xe1000000–0xe33fffff`; `0x9c000000` does not appear in the A52s memory map.
The A52s shim/ADT profile therefore uses `0xe1000000` and size `0x02300000`.
Those values live in `shim/a52s_profile.h`; `tools/mkadt.py` reads that header
instead of carrying a second copy.
