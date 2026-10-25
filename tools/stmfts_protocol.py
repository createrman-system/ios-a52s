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
EVENT_MULTI_TOUCH_DETECTED = 0x02
EVENT_MULTI_TOUCH_ENTER = 0x03
EVENT_MULTI_TOUCH_LEAVE = 0x04
EVENT_MULTI_TOUCH_MOTION = 0x05


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
    # 0x02 only announces that the controller saw multitouch; it has no
    # coordinate payload. Linux stmfts.c reports 0x03/0x05/0x04 only.
    if event_id not in (EVENT_MULTI_TOUCH_ENTER, EVENT_MULTI_TOUCH_LEAVE,
                        EVENT_MULTI_TOUCH_MOTION):
        return None
    slot = (event[0] >> 4) & 0x0F
    if slot >= MAX_FINGERS:
        return None
    x = event[1] | ((event[2] & 0x0F) << 8)
    y = (event[2] >> 4) | (event[3] << 4)
    return Contact(slot, x, y, event[4], event[5], event[7], event[6],
                   event_id != EVENT_MULTI_TOUCH_LEAVE)


def decode_stack(data: bytes) -> list[Contact]:
    if len(data) % EVENT_SIZE:
        raise ValueError("event stack is not aligned to 8-byte events")
    contacts = []
    for i in range(0, len(data), EVENT_SIZE):
        event = data[i:i + EVENT_SIZE]
        # READ_ALL_EVENT's stack ends at the first no-event record. Do not
        # accidentally report stale bytes after the terminator.
        if event[0] == 0:
            break
        contact = decode_event(event)
        if contact is not None:
            contacts.append(contact)
    return contacts


def _self_test() -> None:
    # Slot 2, enter, x=0x321, y=0x654, dimensions and pressure preserved.
    event = bytes([0x23, 0x21, 0x43, 0x65, 7, 5, 0xFE, 9])
    c = decode_event(event)
    assert c == Contact(2, 0x321, 0x654, 7, 5, 9, 0xFE, True)
    release = bytes([0x24, 0, 0, 0, 0, 0, 0, 0])
    assert decode_event(release).down is False
    # Event 0x02 has no usable coordinate payload.
    assert decode_event(bytes([0x22, 0, 0, 0, 0, 0, 0, 0])) is None
    assert decode_event(bytes(EVENT_SIZE)) is None
    # A full hardware stack ends at its no-event record; later bytes are not
    # current contacts even when they happen to resemble a valid event.
    motion = bytes([0x25, 0x22, 0x54, 0x76, 8, 6, 0xFD, 10])
    stale = bytes([0x13, 0x11, 0x11, 0x11, 1, 1, 0, 1])
    assert decode_stack(event + motion + release + bytes(EVENT_SIZE) + stale) == [
        Contact(2, 0x321, 0x654, 7, 5, 9, 0xFE, True),
        Contact(2, 0x422, 0x765, 8, 6, 10, 0xFD, True),
        Contact(2, 0, 0, 0, 0, 0, 0, False),
    ]


if __name__ == "__main__":
    _self_test()
    print("STM FTS protocol self-test: PASS")
