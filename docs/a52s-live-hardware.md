# Galaxy A52s live hardware evidence

Source: root ADB on model `SM-A528B`, plus `a52s-live.dtb` captured on
2026-10-23. The DTB and device dumps are local-only artifacts and are not
committed.

Confirmed:

- UFS host `0x01d84000`, boot device `1d84000.ufshc`; UFS PHY `0x01d87000`;
- GICD `0x17a00000`, GICR `0x17a60000`, timer 19.2 MHz;
- MDSS `0x0ae00000`;
- QUPv3 SE8 I²C `0x00a94000`, `qcom,i2c-geni`;
- touchscreen `stm,stm_ts` at I²C address `0x49`;
- touchscreen IRQ GPIO 81;
- touchscreen AVDD: PM8350C LDO7 (`regulator-pm8350c-l7`);
- touchscreen dimensions: `0x1000 × 0x1000`;
- firmware: `tsp_stm/fts5cu56a_a52sxq.bin`;
- USB DWC3 `0x0a600000`;
- live-DT splash region: `0xe1000000`, size `0x02300000`.
- DRM reports the primary panel modes `1080x2400x120x184672cmdHS` and
  `1080x2400x60x184672cmdHS`.

The live `/proc/iomem` confirms the framebuffer reservation as
`0xe1000000–0xe33fffff`; `0x9c000000` does not appear in the A52s memory map.
The A52s shim/ADT profile therefore uses `0xe1000000` and size `0x02300000`.
