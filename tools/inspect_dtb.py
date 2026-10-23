#!/usr/bin/env python3
"""Print selected properties from a flattened Linux device tree."""
import struct
import sys

blob = open(sys.argv[1], "rb").read()
magic, total, off_struct, off_strings = struct.unpack_from(">4I", blob, 0)
size_strings, size_struct = struct.unpack_from(">2I", blob, 32)
assert magic == 0xD00DFEED
strings = blob[off_strings:off_strings + size_strings]
pos = off_struct
stack = []
interesting = ("touchscreen@49", "i2c@a94000", "stm_ts", "splash_region",
               "reserved-memory", "memory@", "mdss")
while pos < off_struct + size_struct:
    token = struct.unpack_from(">I", blob, pos)[0]
    pos += 4
    if token == 1:
        end = blob.index(0, pos)
        stack.append(blob[pos:end].decode("latin1"))
        pos = (end + 4) & ~3
    elif token == 2:
        stack.pop()
    elif token == 3:
        length, name_off = struct.unpack_from(">2I", blob, pos)
        pos += 8
        value = blob[pos:pos + length]
        pos = (pos + length + 3) & ~3
        end = strings.find(b"\0", name_off)
        key = strings[name_off:end].decode("latin1")
        path = "/" + "/".join(stack)
        selected_phandle = key == "phandle" and value in {bytes.fromhex(x) for x in ("000001e7", "000001fb", "000001fc", "000005b9", "000005ba", "00000303")}
        selected_node = any(x in path.lower() for x in ("qupv3_1_geni_se", "stm_attn_irq", "stm_attn_input"))
        if selected_phandle or selected_node or any(x.lower() in (path + key).lower() for x in interesting):
            print(path, key, value.hex(), repr(value[:120]))
    elif token == 4:
        pass
    elif token == 9:
        break
    else:
        raise RuntimeError(f"bad FDT token {token:#x} at {pos:#x}")
