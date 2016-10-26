#!/usr/bin/env python2.7

import os
import re
import socket
import json
import time
import sys

from options import read_file


class KeyMapper:
    def __init__(self):
        self.keymap_data = ""
        self.keymap_file = "keymap"
        self.main()

    def get_interpret_section(self, stroke):
        re_stroke = stroke.replace("+", "\+").replace("(", "\(").replace(")", "\)")
        interpret_section = re.search(r"interpret *" + re_stroke + r" *\{[^}]*\}( |\n)*;", self.keymap_data).group(0)
        return interpret_section

    def get_xkb_code(self, key_code):
        key_codes = self.get_xkb_keycodes_section()
        key_code_search = re.search(r"<.{2,6}> *= *" + str(key_code) + r" *;", key_codes).group(0)
        xkb_code = key_code_search.split("=")[0].strip(' ')[1:-1]
        return xkb_code

    def get_xkb_keycodes_section(self):
        return re.search(r"xkb_keycodes *\".*\" *\{[^}]*\}", self.keymap_data).group(0)

    def get_xkb_symbols_section(self):
        return re.search(r"xkb_symbols *\".*\" *\{([^{]+(name|key)[^{]+\{[^}]+\};)*", self.keymap_data).group(0)

    def get_keysym_section(self, xkb_code):
        xkb_code = xkb_code.upper()
        return re.search(r"key <" + xkb_code + r"> \{[^}]*\};", self.keymap_data).group(0)

    def get_unused_xkb_codes(self):
        all_codes = self.get_xkb_codes()
        codes = []
        xkb_symbols_section = self.get_xkb_symbols_section()
        for xkb_code in all_codes:
            if xkb_code not in xkb_symbols_section:
                codes.append(xkb_code)
        return codes

    def get_xkb_codes(self):
        codes = []
        for i in range(9, 255):
            try:
                xkb_code = self.get_xkb_code(i)
                codes.append(xkb_code)
            except AttributeError as e:
                print "Key code #" + str(i) + " has no xkb_code defined in xkb_keymap."
        return codes

    def add_overlay_key(self, xkb_code, overlay_xkb_code, num_overlay):
        old_key_def = new_key_def = self.get_keysym_section(xkb_code)
        if "overlay" in old_key_def:
            old_overlay = re.search(r",\n *overlay[0-9] *= *<.{2,6}>", old_key_def).group(0)
            new_key_def = new_key_def.replace(old_overlay, "")
            print xkb_code + " CAN NOT HAVE ANOTHER OVERLAY. DELETING PREVIOUS OVERLAY!"
        new_key_def = new_key_def.replace("}", ",\n overlay" + str(num_overlay) + " = <" + overlay_xkb_code + "> \n}")
        self.keymap_data = self.keymap_data.replace(old_key_def, new_key_def)

    def map_overlays(self, mapping_data, num_overlay):
        # add overlays to keys
        for mapping in mapping_data:
            if "mapped_xkb_code" in mapping:
                code = mapping["key_code"]
                overlay_xkb_code = mapping["mapped_xkb_code"]
                xkb_code = self.get_xkb_code(code)
                self.add_overlay_key(xkb_code, overlay_xkb_code, num_overlay)


    def disable_overlay_key_toggling(self, num_overlay):
        num_overlay = str(num_overlay)
        self.keymap_data = self.keymap_data.replace(self.get_interpret_section("Overlay%s_Enable+AnyOfOrNone(all)" % num_overlay),
                                          read_file("assets/interpret_overlay" + num_overlay))

    def set_overlay_enable_key(self, xkb_code, num_overlay):
        # set up modifier key
        cur_caps = self.get_keysym_section(xkb_code)
        keysym = read_file("assets/overlay_enable_keysym").replace("####", xkb_code).replace("$$$$", str(num_overlay))
        self.keymap_data = self.keymap_data.replace(cur_caps, keysym)

    def create_keysym_sections(self, mapping_data):
        available_key_codes = self.get_unused_xkb_codes()
        # Use available xkb_codes to map user defined key strokes
        for mapping in mapping_data:
            if "mapped_xkb_code" not in mapping:
                overlay_key = mapping["overlay_key"]
                if len(available_key_codes) == 0:
                    print "============================================================"
                    print "NO FREE KEY CODES AVAILABLE FOR MAPPING!!! "
                    print "please log back again"
                    print "you may also have exceeded the number of available key codes"
                    print "============================================================"
                    break
                else:
                    xkb_code = available_key_codes.pop()
                    print "Found free (unused) xkb_code and mapping it now: " + xkb_code
                    mapping["mapped_xkb_code"] = xkb_code
                    new_key_data = "\n key <" + xkb_code + "> {[" + overlay_key + "]};"
                    xkb_symbols_section = old_xkb_symbols_section = self.get_xkb_symbols_section()
                    xkb_symbols_section += new_key_data
                    self.keymap_data = self.keymap_data.replace(old_xkb_symbols_section, xkb_symbols_section)

    def update_keymap(self):
        self.capture_keymap(self.keymap_file)
        config = json.loads(read_file("config.json"))

        def update_overlay(num_overlay):
            overlay = "overlay" + str(num_overlay)
            if config[overlay]["xkb_code"] != "disabled":
                self.create_keysym_sections(config[overlay]["mapping"])
                self.set_overlay_enable_key(config[overlay]["xkb_code"], num_overlay)
                self.map_overlays(config[overlay]["mapping"], num_overlay)
                if config[overlay]["mode"] == "hold":
                    self.disable_overlay_key_toggling(num_overlay)

        update_overlay(1)
        update_overlay(2)

        with open(self.keymap_file, "w") as f:
            f.write(self.keymap_data)
        self.load_keymap_file(self.keymap_file)

    def capture_keymap(self, filename):
        os.system("xkbcomp -xkb $DISPLAY " + filename)
        self.keymap_data = read_file(filename)

    def load_keymap_file(self, filename):
        print "Applying keymap settings..."
        if "rror" not in os.popen("xkbcomp -xkb %s $DISPLAY" % filename).read():
            print "Successfully applied settings."
            os.remove(filename)

    def main(self):
        #if "nosleep" not in sys.argv:
        #    time.sleep(5)

        os.chdir(os.path.dirname(__file__))
        self.update_keymap()

        try:
            s = socket.socket()
            s.bind(("localhost", 24679))
            s.listen(1)

            while True:
                try:
                    s.accept()
                    time.sleep(5)
                    self.load_keymap_file(self.keymap_file)
                except KeyboardInterrupt:
                    break
        except Exception as e:
            print e
            print "Another instance of this Software is already running. Kill it with 'pkill python2.7'."


KeyMapper()
