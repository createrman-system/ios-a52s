# Porting iOS 16 to the Samsung Galaxy A52s 5G

Target: Samsung Galaxy A52s 5G, codename `a52sxq` (also `a52sxqzt` and
`a52sxqks`), models including SM-A528B and SM-A528N. The project repository is
`createrman-system/ios-a52s`.

## Verified project inputs

The workspace contains Simon1511's Android device tree and SM7325 kernel tree,
plus the A52s TWRP tree under `GalaxyA52sFolders/`. Those trees identify:

- Qualcomm SM7325 / Snapdragon 778G 5G, Kryo 670, eight CPUs;
- 1080×2400, 120 Hz AMOLED display;
- UFS 2.1 storage and Samsung's dynamic-partition layout;
- Samsung `stm_ts` touchscreen support and A52s firmware;
- boot/recovery packaging compatible with the Samsung device tree.

## Port status

The A52s has passed early XNU platform initialization with the high-memory
payload and timer-access workaround. The screen subsequently remains static;
the next diagnostic is the persistent log collected from recovery after a
temporary boot. No partition write is required or authorized for this step.

The live `SM-A528B` evidence is recorded in
[`a52s-live-hardware.md`](a52s-live-hardware.md). In particular, the splash
reservation is `0xe1000000` / `0x02300000` (not the Sweet/A71 `0x9c000000`),
UFS is `0x01d84000` on IRQ 297, and the panel is 1080×2400 command mode.

The current XNU touch patch is only an incomplete conversion: it still carries
the A71 SE7, PM6150/L11C, reset and `sec_ts` assumptions. It must be replaced
by an STM FTS5CU56A path for `qcom,i2c-geni@0x00a94000`, address `0x49`, IRQ
GPIO 81, and PM8350C LDO7. The A52s DT specifies no reset GPIO and explicitly
marks DVDD unused, so neither an A71 reset pulse nor its PMIC-GPIO writes are
valid on this handset.

## Bring-up order

1. Extract and preserve the A52s boot/recovery DT and partition backups.
2. Add an A52s hardware profile to `tools/mkadt.py` and the shim.
3. Replace the A71 `sec_ts` path with the A52s `stm_ts` protocol and power
   sequence, using the Android tree as the register-level reference.
4. Build and run QEMU/unit checks where possible.
5. Use a temporary boot/recovery path for the first handset test. Do not flash
   `userdata` or any partition until the user explicitly confirms that step.

The iOS root, when eventually authorized, belongs in the existing `userdata`
partition; no GPT changes are required. Bootloaders, recovery, modem, persist,
and all backups remain protected.
