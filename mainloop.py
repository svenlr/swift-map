#!/usr/bin/env python2.7

import os
import re
import socket
import json
import time
import sys

from options import read_file


def load_keymap(filename):
    os.system("xkbcomp -xkb $DISPLAY " + filename)
    return read_file(filename)


def apply_keymap(filename, keymap_data):
    with open(filename, "w") as f:
        f.write(keymap_data)
    os.system("xkbcomp -xkb %s $DISPLAY" % filename)


def get_interpret(keymap_data, stroke):
    re_stroke = stroke.replace("+", "\+").replace("(", "\(").replace(")", "\)")
    interpret_section = re.search(r"interpret *" + re_stroke + r" *\{[^}]*\}( |\n)*;", keymap_data).group(0)
    print interpret_section
    return interpret_section


def get_key_definition(keymap_data, xkb_code):
    xkb_code = xkb_code.upper()
    return re.search(r"key <" + xkb_code + r"> \{[^}]*\};", keymap_data).group(0)


def get_xkb_code(keymap_data, key_code):
    key_codes = re.search(r"xkb_keycodes *\".*\" *\{[^}]*\}", keymap_data).group(0)
    key_code_search = re.search(r"<.{2,6}> *= *" + str(key_code) + r" *;", key_codes).group(0)
    xkb_code = key_code_search.split("=")[0].strip(' ')[1:-1]
    return xkb_code


def get_xkb_symbols_section(keymap_data):
    return re.search(r"xkb_symbols *\".*\" *\{([^{]+(name|key)[^{]+\{[^}]+\};)*", keymap_data).group(0)


def add_overlay_key(keymap_data, xkb_code, overlay_xkb_code):
    old_key_def = new_key_def = get_key_definition(keymap_data, xkb_code)
    new_key_def = new_key_def.replace("}", ",\n    overlay1 = <" + overlay_xkb_code + "> \n}")
    keymap_data = keymap_data.replace(old_key_def, new_key_def)
    return keymap_data


def update_keymap():
    keymap_data = load_keymap("keymap")

    # set up modifier keys
    cur_caps = get_key_definition(keymap_data, "CAPS")
    keymap_data = keymap_data.replace(cur_caps, read_file("assets/caps_default"))

    config = json.loads(read_file("config.json"))
    mapping_data = config["mapping"]

    available_key_codes = []
    xkb_symbols_section = get_xkb_symbols_section(keymap_data)
    for i in range(9, 255):
        try:
            xkb_code = get_xkb_code(keymap_data, i)
            if xkb_code not in xkb_symbols_section:
                print "No Symbols defined: " + xkb_code
                available_key_codes.append(xkb_code)
        except AttributeError as e:
            print e
            print "Key Code " + str(i) + " is not defined."

    for mapping in mapping_data:
        if "mapped_xkb_code" not in mapping:
            key = mapping["key"]
            if len(available_key_codes) == 0:
                print "NO FREE KEY CODES LEFT FOR MAPPING!!!"
                break
            else:
                xkb_code = available_key_codes.pop()
                print xkb_code
                mapping["mapped_xkb_code"] = xkb_code
                new_key_data = "\n key <" + xkb_code + "> {[" + key + "]};"
                xkb_symbols_section = old_xkb_symbols_section = get_xkb_symbols_section(keymap_data)
                xkb_symbols_section += new_key_data
                keymap_data = keymap_data.replace(old_xkb_symbols_section, xkb_symbols_section)

    for mapping in mapping_data:
        if "mapped_xkb_code" in mapping:
            code = mapping["code"]
            xkb_code = get_xkb_code(keymap_data, code)
            overlay_xkb_code = mapping["mapped_xkb_code"]
            keymap_data = add_overlay_key(keymap_data, xkb_code, overlay_xkb_code)

    keymap_data = keymap_data.replace(get_interpret(keymap_data, "Overlay1_Enable+AnyOfOrNone(all)"), read_file("assets/interpret_overlay1"))

    apply_keymap("keymap", keymap_data)

    return keymap_data


def main():
    if "nosleep" not in sys.argv:
        time.sleep(5)

    os.chdir(os.path.dirname(__file__))
    keymap_data = update_keymap()

    s = socket.socket()
    s.bind(("localhost", 24679))
    s.listen(1)

    while True:
        try:
            s.accept()
            apply_keymap("keymap", keymap_data)
        except KeyboardInterrupt:
            break


main()
