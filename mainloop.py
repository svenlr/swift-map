#!/usr/bin/env python2.7

import time
import os
import sys
import re
import socket
import json

from options import get_option, read_file


class KeyMapping:
    def __init__(self, mapping_data, original_key):
        self.code = mapping_data["code"]
        self.modifiers = mapping_data["modifiers"]
        self.original_key = original_key
        self.mapped_key = mapping_data["key"]


def get_key_definition(map_file, key):
    key = key.upper()
    return re.search(r"key <" + key + r"> \{[^}]*\};", map_file).group(0)


def update_key_definition(map_file, key, value):
    cur_def = get_key_definition(map_file, key)
    symbol_list_search = re.search(r"(?<=symbols).*\[(( ){0,30}.{0,20}( ){0,20},?){0,8}(?=\])", cur_def).group(0)
    group, symbol_list_search = symbol_list_search.split("=")
    group = group.replace("[", "").replace("]", "")
    group = group[0].lower() + group[1:]
    symbol_list = symbol_list_search.strip(' ')
    num_entries = symbol_list.count(",") + 1
    for i in range(num_entries, 8):
        if i == 4 or i == 5:
            symbol_list += ", " + str(value)
        else:
            symbol_list += ", NoSymbol"
    symbol_list += "]"
    print symbol_list
    type_search = re.search(r"type(\[" + group + r"\])( )*=( )*\"(_|[A-Z]{0,20}){0,10}\"", cur_def)
    if not type_search:
        type_search = re.search(r"type( )*=( )*\"(_|[A-Z]{0,20}){0,10}\"", cur_def)
    type_key = type_search.group(0).split("=")[0]
    cur_def = cur_def.replace(symbol_list_search, symbol_list)
    cur_def = cur_def.replace(type_search.group(0), type_key + "=\"EIGHT_LEVEL_SEMIALPHABETIC\"")
    print cur_def


def update_keymap():
    keymap = {}
    os.system("xkbcomp -xkb $DISPLAY keymap")
    with open("test") as f:
        keymap_file = f.read()
    with open("config.json") as f:
        config = json.loads(f.read())
    keymap_data = config["keymap"]
    modifiers = []
    cur_caps = get_key_definition(keymap_file, "CAPS")
    cur_mode_switch = get_key_definition(keymap_file, "MDSW")
    cur_mod_map = re.search(r"modifier_map .{3,8} \{.*\n?.*<MDSW>.*\n?.*\}", keymap_file).group(0)
    keymap_file = keymap_file.replace(cur_caps, read_file("assets/caps_default"))
    keymap_file = keymap_file.replace(cur_mode_switch, read_file("assets/mdsw_default"))
    keymap_file = keymap_file.replace(cur_mod_map, "modifier_map Mod3 { <MDSW> }")
    update_key_definition(keymap_file, "AC02", "Up")
    for mapping in keymap_data:
        try:
            for mod in mapping["modifiers"]:
                if mod not in modifiers:
                    modifiers.append(mod)
            code = mapping["code"]
            original_key = get_option("Xmodmap_tmp", "keycode " + str(code)).split(" ")[0]
            if code not in keymap:
                keymap[code] = []
            keymap[code].append(KeyMapping(mapping, original_key))
            os.system("xmodmap \"keycode %s = %s %s %s %s\"" % (str(code), original_key, original_key.upper(),
                                                                original_key, original_key.upper()))
        except Exception as e:
            print e
    for mod in modifiers:
        os.system("xmodmap \"keycode %s = NoSymbol\"" % (str(mod)))


    with open("keymap", "w") as f:
        f.write(keymap_file)

    return keymap


def main():
    # if "nosleep" not in sys.argv:
    #    time.sleep(5)

    os.chdir(os.path.dirname(__file__))
    keymap = update_keymap()

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
