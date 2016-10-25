#!/usr/bin/env python2.7

import time
import os
import threading
import pyxhook
import socket

time.sleep(5)

os.chdir(os.path.dirname(__file__))
os.system("xmodmap Xmodmap")

mod_release_lock = threading.Lock()
pressed_keys = []

# whether Level 5 Shift (Caps Lock) is pressed
level5shift = False

def reactivate_mod():
    os.popen("xdotool keydown --delay 0 ISO_Level3_Shift")


def clear_mod():
    os.popen("xdotool keyup --delay 0 ISO_Level3_Shift")


def keyPress(key):
    global mod_release_lock
    mod_release_lock.acquire()
    clear_mod()
    os.popen("xdotool key --delay 0 " + key)
    reactivate_mod()
    mod_release_lock.release()
    pass


def generate_key_event(key, eventType):
    if eventType == "key down":
        if level5shift:
            if not key in pressed_keys: pressed_keys.append(key)
            keyPress(key)
            for i in range(100):
                time.sleep(0.004)
                if not key in pressed_keys:
                    return
            while key in pressed_keys:
                keyPress(key)
                time.sleep(0.017)
    else:
        while key in pressed_keys:
            pressed_keys.remove(key)


def handle_key_event(event):
    global mod_release_lock
    global level5shift

    # the key to be pressed as replacement for this keyboard event
    replacement_key = None

    if event.ScanCode == 66:  # caps lock key code
        # level5shift key
        if event.MessageName == "key down":
            level5shift = True
        elif event.MessageName == "key up":
            if mod_release_lock.acquire(False):
                level5shift = False
                os.system("xdotool keyup ISO_Level3_Shift")
                mod_release_lock.release()
    elif event.ScanCode == 31:  # i key
        replacement_key = "Up"
    elif event.ScanCode == 44:  # j key
        replacement_key = "Left"
    elif event.ScanCode == 45:  # k key
        replacement_key = "Down"
    elif event.ScanCode == 46:  # l key
        replacement_key = "Right"
    elif event.ScanCode == 47:  # oe
        replacement_key = "End"
    elif event.ScanCode == 43:  # h
        replacement_key = "Home"
    elif event.ScanCode == 30:  # u
        replacement_key = "Page_Up"
    elif event.ScanCode == 32:  # o
        replacement_key = "Page_Down"

    if replacement_key is not None:
        threading.Thread(None, lambda: generate_key_event(replacement_key, event.MessageName)).start()


hookman = pyxhook.HookManager()
hookman.KeyDown = handle_key_event
hookman.KeyUp = handle_key_event
hookman.HookKeyboard()
hookman.start()

s = socket.socket()
s.bind(("localhost", 24679))
s.listen(1)

while True:
    try:
        s.accept()
        os.system("xmodmap Xmodmap")
        print "test"
    except KeyboardInterrupt:
        break

hookman.cancel()
