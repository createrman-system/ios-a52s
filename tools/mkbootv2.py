#!/usr/bin/env python3
"""Pack kernel, ramdisk, and dtb into an Android boot image header version 2.

Usage:
    python mkbootv2.py --kernel KERNEL --ramdisk RAMDISK --dtb DTB -o OUT_BOOT_IMG
                       [--cmdline CMD] [--base BASE] [--kernel_offset KOFF]
                       [--ramdisk_offset ROFF] [--tags_offset TOFF] [--dtb_offset DOFF]
                       [--pagesize PS] [--os_version VER] [--os_patch_level PATCH]
"""

import argparse
import os
import struct
import sys

def pad(n, page_size):
    return (n + page_size - 1) // page_size * page_size

def pack_boot_v2(kernel_path, ramdisk_path, dtb_path, out_path,
                 cmdline="", base=0, kernel_offset=0x8000, ramdisk_offset=0x2000000,
                 tags_offset=0x1e00000, dtb_offset=0x1f00000, page_size=4096,
                 os_version="17.0.0", os_patch_level="2035-06"):

    with open(kernel_path, 'rb') as f:
        kernel = f.read()
    with open(ramdisk_path, 'rb') as f:
        ramdisk = f.read()
    with open(dtb_path, 'rb') as f:
        dtb = f.read()

    kernel_size = len(kernel)
    ramdisk_size = len(ramdisk)
    second_size = 0
    dtb_size = len(dtb)

    kernel_addr = base + kernel_offset
    ramdisk_addr = base + ramdisk_offset
    second_addr = 0
    tags_addr = base + tags_offset
    dtb_addr = base + dtb_offset

    header_version = 2
    os_version_raw = 0x16000182  # Android 10/11 default

    magic = b'ANDROID!'
    name = b'\0' * 16

    cmdline_bytes = cmdline.encode('utf-8')
    cmdline_main = cmdline_bytes[:512].ljust(512, b'\0')
    cmdline_extra = cmdline_bytes[512:1536].ljust(1024, b'\0')

    header_id = b'\0' * 32
    recovery_dtbo_size = 0
    recovery_dtbo_offset = 0
    header_size = 1660

    header = bytearray(page_size)

    # Base header v0
    struct.pack_into('<8s10I16s512s32s1024s', header, 0,
                     magic, kernel_size, kernel_addr, ramdisk_size, ramdisk_addr,
                     second_size, second_addr, tags_addr, page_size,
                     header_version, os_version_raw, name, cmdline_main,
                     header_id, cmdline_extra)

    # Header v1 fields (at offset 1632)
    struct.pack_into('<IQI', header, 1632,
                     recovery_dtbo_size, recovery_dtbo_offset, header_size)

    # Header v2 fields (at offset 1648)
    struct.pack_into('<IQ', header, 1648,
                     dtb_size, dtb_addr)

    with open(out_path, 'wb') as out:
        out.write(header)
        out.write(kernel)
        out.write(b'\0' * (pad(kernel_size, page_size) - kernel_size))
        out.write(ramdisk)
        out.write(b'\0' * (pad(ramdisk_size, page_size) - ramdisk_size))
        out.write(dtb)
        out.write(b'\0' * (pad(dtb_size, page_size) - dtb_size))

    print(f"Packed {out_path} (v2, size {os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pack Android boot image v2")
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--ramdisk", required=True)
    parser.add_argument("--dtb", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--cmdline", default="console=null")
    parser.add_argument("--base", type=lambda x: int(x, 0), default=0)
    parser.add_argument("--kernel_offset", type=lambda x: int(x, 0), default=0x8000)
    parser.add_argument("--ramdisk_offset", type=lambda x: int(x, 0), default=0x2000000)
    parser.add_argument("--tags_offset", type=lambda x: int(x, 0), default=0x1e00000)
    parser.add_argument("--dtb_offset", type=lambda x: int(x, 0), default=0x1f00000)
    parser.add_argument("--pagesize", type=lambda x: int(x, 0), default=4096)
    args = parser.parse_args()

    pack_boot_v2(args.kernel, args.ramdisk, args.dtb, args.output,
                 cmdline=args.cmdline, base=args.base,
                 kernel_offset=args.kernel_offset,
                 ramdisk_offset=args.ramdisk_offset,
                 tags_offset=args.tags_offset,
                 dtb_offset=args.dtb_offset,
                 page_size=args.pagesize)
