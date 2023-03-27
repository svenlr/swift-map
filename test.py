import Xlib

import mainloop


def key_faker_test():
    key_faker = mainloop.KeyFaker()
    command_overlay = mainloop.CommandOverlay(0, 23, "hold")
    print(Xlib.XK.string_to_keysym("NoSymbol"))
    command_overlay.execute_command_sequence([
        {"text": '{'}
    ])


if __name__ == "__main__":
    key_faker_test()
