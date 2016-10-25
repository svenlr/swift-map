#!/usr/bin/env python2.7

import time
import os
import threading
import pyxhook
import socket

# whether (Caps Lock) is pressed
modifier = False
modifier_lock = threading.Lock()

# whether caps key down was generated last_time and a lock for the boolean
caps_down_generated = False
caps_down_generate_lock = threading.Lock()

caps_up_generated = False
caps_up_generate_lock = threading.Lock()


def main():
    time.sleep(5)

    os.chdir(os.path.dirname(__file__))
    os.system("xmodmap Xmodmap")

    hook_manager = pyxhook.HookManager()
    hook_manager.KeyDown = handle_key_event
    hook_manager.KeyUp = handle_key_event
    hook_manager.HookKeyboard()
    hook_manager.start()

    s = socket.socket()
    s.bind(("localhost", 24679))
    s.listen(1)

    while True:
        try:
            s.accept()
            os.system("xmodmap Xmodmap")
        except KeyboardInterrupt:
            break

    hook_manager.cancel()


def reactivate_modifier():
    global caps_down_generated, caps_down_generate_lock
    with caps_down_generate_lock:
        caps_down_generated = True
        os.system("xdotool keydown --delay 0 ISO_Level3_Shift")


def clear_modifier():
    global caps_up_generated, caps_up_generate_lock
    with caps_up_generate_lock:
        caps_up_generated = True
        os.system("xdotool keyup --delay 0 ISO_Level3_Shift")


def generate_key_event(key, event):
    event = event.replace(" ", "")  # key down -> keydown
    global modifier_lock
    modifier_lock.acquire()
    if modifier:
        if event == "keydown":
            clear_modifier()
        os.system("xdotool %s --delay 0 %s" % (event, key))
        if event == "keyup":
            reactivate_modifier()
    modifier_lock.release()


def handle_key_event(event):
    global modifier, modifier_lock
    global caps_up_generated, caps_down_generated, caps_down_generate_lock, caps_up_generate_lock

    # the key to be pressed as replacement for the event's key
    replacement_key = None

    if event.ScanCode == 66:  # caps key
        if event.MessageName == "key down":
            with caps_down_generate_lock:
                generated = caps_down_generated
                caps_down_generated = False
            if not generated:
                with modifier_lock:
                    modifier = True
        elif event.MessageName == "key up":
            with caps_up_generate_lock:
                generated = caps_up_generated
                caps_up_generated = False
            if not generated:
                with modifier_lock:
                    os.system("xdotool keyup ISO_Level3_Shift")
                    modifier = False
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


main()
