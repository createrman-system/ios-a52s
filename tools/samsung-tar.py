#!/usr/bin/env python3
"""Package boot/recovery images into a Samsung Odin-flashable tarball.

Usage:
    python tools/samsung-tar.py <input_image> [output_tar]
Example:
    python tools/samsung-tar.py out/shim-boot.img out/boot.tar
"""

import os
import sys
import tarfile

def package_odin_tar(src_path: str, out_path: str = None) -> str:
    if not os.path.isfile(src_path):
        print(f"Error: input file '{src_path}' not found.", file=sys.stderr)
        sys.exit(1)

    if not out_path:
        base_name = os.path.splitext(os.path.basename(src_path))[0]
        out_path = f"{base_name}.tar"

    # Samsung Odin requires files inside the tar archive to have standard partition names,
    # e.g., 'boot.img' or 'recovery.img'.
    arcname = "boot.img"
    if "recovery" in os.path.basename(src_path).lower():
        arcname = "recovery.img"

    print(f"Packaging '{src_path}' as '{arcname}' into '{out_path}'...")
    with tarfile.open(out_path, "w", format=tarfile.USTAR_FORMAT) as tar:
        tar.add(src_path, arcname=arcname)

    size = os.path.getsize(out_path)
    print(f"Created Odin-compatible package: {out_path} ({size} bytes)")
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    package_odin_tar(inp, out)
