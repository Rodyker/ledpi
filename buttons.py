#!/usr/bin/python

from inputs import DeviceManager, InputEvent, GamePad

gamepad0: GamePad = DeviceManager().gamepads[0]

while True:
    event: InputEvent
    for event in gamepad0.read():
        if event.ev_type == "Sync":
            continue

        print("{}\t{}\t{}".format(event.code, event.ev_type, event.state))
