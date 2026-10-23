# A52s STM touch implementation plan

The bundled SM7325 kernel contains `drivers/input/touchscreen/stmfts.c` and
the Samsung `drivers/input/sec_input/stm/` implementation. The simpler
`stmfts.c` path is the XNU port reference.

Confirmed protocol:

- controller commands: read-all-events `0x86`, sense-on `0x93`, clear stack
  `0xa1`;
- each event is 8 bytes, with event ID in the low nibble and slot in the high
  nibble of byte 0;
- x = byte 1 + low nibble of byte 2 shifted by 8;
- y = high nibble of byte 2 + byte 3 shifted by 4;
- A52s reports a 4096×4096 coordinate space and up to 10 contacts.

`tools/stmfts_protocol.py` is a host-side executable reference and self-test.
The next kernel patch should reuse these definitions in `sweet_touch.c`, but
must first identify SE8's clock/reset register and pinctrl state. Those values
are not safely inferable from the I²C node alone.
