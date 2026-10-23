# Historical A71 reference

This document is retained as a reference for the earlier A71 work. It is not
the target-device guide for this repository; use `docs/galaxy-a52s-port.md`.

This guide documents the technical details, hardware mappings, and flashing procedures for running Apple's XNU kernel and unmodified iOS 16.7.16 (iPhone X) userland on the **Samsung Galaxy A71 4G (`SM-A715F`)**.

---

## 1. Hardware Architecture & Compatibility

The Galaxy A71 4G (`SM-A715F`) is powered by the **Qualcomm Snapdragon 730 (`SM7150-AA`)**, which belongs to the identical silicon platform family as the Xiaomi Redmi Note 10 Pro (`sweet`, Snapdragon 732G / `SM7150-AC`).

Because both devices share Qualcomm's `SM7150` architecture, the low-level platform code (SMP PSCI boot, GICv3 interrupt tables, system timers, DDR memory banks, and UFS 2.1 host controller) is shared 1:1.

### Verified Hardware Offsets (from LineageOS A71 Kernel Tree)

| Subsystem | Galaxy A71 4G (`SM-A715F`) Mapping | Reference in Kernel Source |
| :--- | :--- | :--- |
| **SoC Platform** | Qualcomm `SM7150` / `sdmmagpie` | `arch/arm64/boot/dts/qcom/sdmmagpie.dtsi` |
| **CPU Cluster** | 2x Kryo 470 Gold (A76) + 6x Silver (A55) | ARM64 PSCI / GICv3 |
| **Framebuffer Base** | `0x9c000000` (Length: `0x01700000` / 23 MiB) | `cont_splash_region@9c000000` |
| **Display Panel** | Super AMOLED Plus, 1080 × 2400 @ 60Hz | Samsung S6E3FA9 FHD+ |
| **Storage Controller**| Qualcomm UFS 2.1 (`ufshc@1d84000`), IRQ `265` | `sdmmagpie.dtsi:2349` |
| **Touchscreen Bus** | QUPv3 Serial Engine 7 (`qupv3_se7_i2c@a84000`)| `sdmmagpie-qupv3.dtsi:314` |
| **Touchscreen IC** | Samsung `sec_ts` (S6SY771) @ slave `0x48` | `sm7150-sec-a71-eur-overlay-r06.dts` |
| **Touchscreen IRQ**| TLMM GPIO `9` (Level High / `0x2008`) | Identical reference GPIO |
| **Power Button** | PM6150 PON (`PON_POWER_ON_TYPE_KPDPWR`) | `pm6150.dtsi:43` |
| **Volume Down** | PM6150 RESIN (`PON_POWER_ON_TYPE_RESIN`) | `pm6150.dtsi:49` |
| **Volume Up** | PM6150 GPIO `2` | `sm7150-sec-a71-eur-overlay-r06.dts:3077` |

*Note: All motherboard revisions (Rev 0.0 through Rev 0.7) share identical memory maps, UFS offsets, framebuffer addresses, and touch GPIO pins.*

---

## 2. Booting & Flashing on Samsung Devices

Unlike Xiaomi devices that support non-destructive memory booting via `fastboot boot <image>`, Samsung devices use **Download Mode (Odin protocol / LOKE)**.

### Bootloader Unlock
1. Enable **Developer Options** (tap Build Number 7 times).
2. Toggle **OEM Unlocking** and **USB Debugging** to ON.
3. Power off the device. Connect the USB cable to a PC while holding **Volume Up + Volume Down** until the teal Warning screen appears.
4. Long-press **Volume Up** to unlock the bootloader (this wipes user data and permanently trips Knox to `0x1`).

### Flashing Options

You have two primary options to boot the custom image on the A71:

#### Method A: Flashing via TWRP (Recommended)
1. Install TWRP for `SM-A715F` along with a disabled `vbmeta.tar` (with `--disable-verity --disable-verification`).
2. Copy `shim-boot.img` onto an SD card or push via ADB:
   ```bash
   adb push out/shim-boot.img /sdcard/
   ```
3. In TWRP, tap **Install** $\rightarrow$ **Install Image** $\rightarrow$ select `shim-boot.img` $\rightarrow$ choose **Boot** partition $\rightarrow$ Swipe to flash.

#### Method B: Flashing via Odin (.tar package)
1. Package the built boot image into a tarball using the helper script:
   ```bash
   python tools/samsung-tar.py out/shim-boot.img out/boot.tar
   ```
2. Reboot the phone into **Download Mode**.
3. In Odin, load `out/boot.tar` into the **AP** slot (and keep a disabled `vbmeta.tar` in the **USERDATA** slot if flashing stock firmware base).
4. Click **Start**.

---

## 3. Preparing the iOS 16 RootFS on `userdata`

Just like on `ios-sweet`, the root filesystem lives on the phone's internal storage:

1. In TWRP terminal (or via `adb shell`):
   ```bash
   # Format userdata as HFS+
   mkfs.hfsplus -v "iOS" /dev/block/bootdevice/by-name/userdata
   ```
2. Follow `tools/mkiosroot.sh` using the iPhone X IPSW (`iPhone10,3`, iOS 16.7.16 `20H392`) to generate the rootfs payload and write it into the partition.

---

## 4. Compiling the Kernel with GitHub Actions

1. In your GitHub repository ([`dmyslisz/ios-a71`](https://github.com/dmyslisz/ios-a71)), go to the **Actions** tab.
2. Select the **xnu** workflow from the sidebar.
3. Click **Run workflow** (default branch: `main`, config: `DEVELOPMENT`, machine: `SWEET`).
4. Once the build finishes (approx. 45–60 minutes on GitHub's macOS cloud runner), download the **`xnu-kernel`** artifact.
