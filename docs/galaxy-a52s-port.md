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

The first A52s handset evidence is now available: model `SM-A528B`, boot
device `1d84000.ufshc`, and the supplied platform map reports GICD
`0x17a00000`, GICR `0x17a60000`, a 19.2 MHz timer, UFS `0x01d84000` IRQ 265,
framebuffer `0x9c000000`, MDSS `0xae000000`, and an STM touchscreen at I2C
address `0x49` on SE8 at `0x00a94000`.

The live `/proc/iomem` confirms UFS `0x01d84000–0x01d86fff`, UFS PHY at
`0x01d87000`, UFS ICE at `0x01d88000`, DWC3 at `0x0a600000`, and pinctrl at
`0x0f000000`. Root ADB access is available. The captured device-tree archive
was produced through a Windows shell redirection and is not a valid binary
tarball, so a raw DTB pull is still needed.

The ADT identity/CPU profile now reflects SM7325/Kryo 670 and the shim/UFS
comments identify the A52s addresses. The touch driver is deliberately not
switched from the old S6SY771 implementation yet: A52s uses STM `stm_ts`, so
it needs a separate protocol and power-sequencing implementation.

The XNU port currently still contains the proven Sweet/A71 low-level driver
implementation. It is not A52s-ready yet. The following values must be read
from an A52s booted in recovery/Download mode or from a live A52s device tree
before a kernel image is tested:

1. bootloader-provided framebuffer base, stride, format and reserved size;
2. GIC distributor/redistributor addresses and timer frequency;
3. UFS controller base and interrupt;
4. QUP/GENI serial-engine base and the `stm_ts` bus/address;
5. touch reset, IRQ and regulator GPIOs;
6. RAM banks and Qualcomm reserved-memory/XPU carve-outs.

The existing `0x9c000000` framebuffer, SM7150 MMIO addresses, A71 S6SY771
driver, and A71 GPIO numbers are therefore reference values only. They must not
be used for A52s flashing.

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
