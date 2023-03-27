#!/usr/bin/env python3

import os
import socket
import sys
import time
from swiftmap import SwiftMap

try:
    import pyxhook
    import Xlib, Xlib.protocol, Xlib.display, Xlib.X

    enable_cmd_overlays = True
except Exception as e:
    pyxhook = Xlib = None
    enable_cmd_overlays = False
    print("Warning:")
    print(e)
    print("No X library support. Snippets and commands are not supported without python-xlib.")
    print("You can still use key remapping as usual.")
    print("You may want to install python-xlib.")
    time.sleep(1)

default_path = os.path.dirname(__file__)
os.chdir(default_path)


def main():
    global enable_cmd_overlays

    if "nosleep" not in sys.argv:
        print("Waiting 5 seconds. Use nosleep arguments to disable.")
        time.sleep(5)

    if "nocmdoverlay" in sys.argv or "noloop" in sys.argv:
        print("Command overlays are disabled.")
        enable_cmd_overlays = False

    swift_map = SwiftMap(enable_cmd_overlays=enable_cmd_overlays)

    swift_map.configure_keymap()
    os.system("gsettings set org.gnome.settings-daemon.plugins.keyboard active false")

    if "noloop" not in sys.argv:
        print("\n Entering forever loop. Waiting for resume script to trigger re-apply of keymap after suspend... ")
        if enable_cmd_overlays:
            print("Note: CMD Overlays are enabled. Observing keyboard to trigger command overlay functionality...")
        print("This can be disabled with the argument noloop on command line.")

        try:
            s = socket.socket()
            s.bind(("localhost", 24679))
            s.listen(1)

            for overlay in swift_map.cmd_overlays:
                overlay.start_hooking_keyboard()

            while True:
                try:
                    # as soon as we receive an incoming connection, a reload of the keymap is triggered.
                    s.accept()
                    swift_map.keymap.apply_to_system()
                except KeyboardInterrupt:
                    for overlay in swift_map.cmd_overlays:
                        overlay.stop_hooking_keyboard()
                    break
        except Exception as e:
            print(e, ". Another instance of this program is already running. Kill it and "
                     "restart the program if you want suspend/resume and command overlays to work correctly.")


if __name__ == "__main__":
    main()
