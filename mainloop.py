#!/usr/bin/env python2.7

import os
import re
import socket
import json

from options import read_file


class KeyMapping:
    def __init__(self, mapping_data, original_key):
        self.code = mapping_data["code"]
        self.modifiers = mapping_data["modifiers"]
        self.original_key = original_key
        self.mapped_key = mapping_data["key"]


def get_xkb_code(keymap_data, key_code):
    key_codes = re.search(r"xkb_keycodes *\".*\" *\{[^}]*\}", keymap_data).group(0)
    key_code_search = re.search(r"<.{2,6}> *= *" + str(key_code) + r" *;", key_codes).group(0)
    xkb_code = key_code_search.split("=")[0].strip(' ')[1:-1]
    return xkb_code


def load_keymap(filename):
    os.system("xkbcomp -xkb $DISPLAY " + filename)
    return read_file(filename)


def apply_keymap(filename, keymap_data):
    with open(filename, "w") as f:
        f.write(keymap_data)
    os.system("xkbcomp -xkb %s $DISPLAY" % filename)


def get_key_definition(keymap_data, xkb_code):
    xkb_code = xkb_code.upper()
    return re.search(r"key <" + xkb_code + r"> \{[^}]*\};", keymap_data).group(0)


def update_key_definition(keymap_data, xkb_code, key):
    old_key_def = new_key_def = get_key_definition(keymap_data, xkb_code)
    symbol_list_search = re.search(r"(?<=symbols).*\[(( ){0,30}.{0,20}( ){0,20},?){0,8}\]", new_key_def).group(0)
    group, old_symbol_list = symbol_list_search.split("=")
    group = group.strip(' ')[1:-1]
    group = group[0].lower() + group[1:]
    old_symbol_list = old_symbol_list.replace("[", "").replace("]", "").strip(' ')
    symbol_list = old_symbol_list
    print symbol_list
    entries = symbol_list.split(',')
    symbol_list = entries[0]
    for i in range(1, 8):
        if i == 4 or i == 5:
            symbol_list += ", " + str(key)
        elif i < len(entries):
            symbol_list += ", " + str(entries[i])
        else:
            symbol_list += ", NoSymbol"
    print symbol_list
    type_search = re.search(r"type(\[" + group + r"\])( )*=( )*\"(_|[A-Z]{0,20}){0,10}\"", new_key_def)
    if not type_search:
        type_search = re.search(r"type( )*=( )*\"(_|[A-Z]{0,20}){0,10}\"", new_key_def)
    type_key = type_search.group(0).split("=")[0]
    new_key_def = new_key_def.replace(old_symbol_list, symbol_list)
    new_key_def = new_key_def.replace(type_search.group(0), type_key + "=\"EIGHT_LEVEL_SEMIALPHABETIC\"")
    keymap_data = keymap_data.replace(old_key_def, new_key_def)
    return keymap_data


def update_keymap():
    keymap = {}
    keymap_data = load_keymap("keymap")

    # set up modifier keys
    cur_caps = get_key_definition(keymap_data, "CAPS")
    cur_mode_switch = get_key_definition(keymap_data, "MDSW")
    cur_mod_map = re.search(r"modifier_map .{3,8} \{[^}]*<MDSW>[^}]*\}", keymap_data).group(0)
    keymap_data = keymap_data.replace(cur_caps, read_file("assets/caps_default"))
    keymap_data = keymap_data.replace(cur_mode_switch, read_file("assets/mdsw_default"))
    keymap_data = keymap_data.replace(cur_mod_map, "modifier_map Mod3 { <MDSW> }")

    config = json.loads(read_file("config.json"))
    mapping_data = config["mapping"]

    for mapping in mapping_data:
        code = mapping["code"]
        xkb_code = get_xkb_code(keymap_data, code)
        print code, xkb_code
        replacement_key = mapping["key"]
        keymap_data = update_key_definition(keymap_data, xkb_code, replacement_key)

    apply_keymap("keymap", keymap_data)

    return keymap


def main():
    # if "nosleep" not in sys.argv:
    #    time.sleep(5)

    os.chdir(os.path.dirname(__file__))
    update_keymap()

    s = socket.socket()
    s.bind(("localhost", 24679))
    s.listen(1)

    while True:
        try:
            s.accept()
            os.system("xmodmap Xmodmap")
        except KeyboardInterrupt:
            break


main()
