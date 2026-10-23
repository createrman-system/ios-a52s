#!/usr/bin/env python3
"""Decode the 8-byte STM FTS event format used by the Galaxy A52s.

This is a host-side reference for the XNU driver. The Linux driver in the
bundled SM7325 source uses the same command and event definitions.
"""
from dataclasses import dataclass

READ_ALL_EVENT = 0x86
SENSE_ON = 0x93
CLEAR_EVENT_STACK = 0xA1
EVENT_SIZE = 8
MAX_FINGERS = 10


@dataclass(frozen=True)
class Contact:
    slot: int
    x: int
    y: int
    major: int
    minor: int
    pressure: int
    orientation: int
    down: bool


def decode_event(event: bytes) -> Contact | None:
    if len(event) != EVENT_SIZE:
        raise ValueError("STM FTS events are exactly 8 bytes")
    event_id = event[0] & 0x0F
    if event_id not in (0x02, 0x03, 0x04, 0x05):
        return None
    slot = (event[0] >> 4) & 0x0F
    if slot >= MAX_FINGERS:
        return None
    x = event[1] | ((event[2] & 0x0F) << 8)
    y = (event[2] >> 4) | (event[3] << 4)
    return Contact(slot, x, y, event[4], event[5], event[7], event[6], event_id != 0x04)


def decode_stack(data: bytes) -> list[Contact]:
    if len(data) % EVENT_SIZE:
        raise ValueError("event stack is not aligned to 8-byte events")
    return [c for i in range(0, len(data), EVENT_SIZE)
            if (c := decode_event(data[i:i + EVENT_SIZE])) is not None]


def _self_test() -> None:
    # slot 2, enter, x=0x321, y=0x654, dimensions and pressure preserved.
    event = bytes([0x23, 0x21, 0x43, 0x65, 7, 5, 0xFE, 9])
    c = decode_event(event)
    assert c == Contact(2, 0x321, 0x654, 7, 5, 9, 0xFE, True)
    release = bytes([0x24, 0, 0, 0, 0, 0, 0, 0])
    assert decode_event(release).down is False
    assert decode_event(bytes(EVENT_SIZE)) is None


if __name__ == "__main__":
    _self_test()
    print("STM FTS protocol self-test: PASS")
