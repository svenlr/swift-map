#!/usr/bin/env python3

import json
import os
import re
import socket
import sys
import time
import itertools

from system_install import generate_keyboard_layout_file_str, get_current_keyboard_layout_id, install_keyboard_layout_file, get_symbols_install_dir, \
    add_layout_to_rules_xml_file

try:
    import pyxhook
    import Xlib, Xlib.protocol, Xlib.display, Xlib.X

    xlib_support = True
except Exception as e:
    pyxhook = Xlib = None
    xlib_support = False
    print("Warning:")
    print(e)
    print("No X library support. Snippets and commands are not supported without python3-xlib.")
    print("You can still use key remapping as usual.")
    print("You may want to install python3-xlib.")
    time.sleep(1)

default_path = os.path.dirname(__file__)
os.chdir(default_path)


def read_file(file_):
    with open(file_) as f:
        return f.read()


class Mapper:
    def __init__(self):
        self.keymap_data = ""
        self.keymap_file = "keymap"

        self.generated_key_labels_file = "assets/generated_key_labels"
        self.used_key_labels = self.restore_used_key_labels()

        self.config = json.loads(read_file("config.json"))

        self.overlays = []

        self.created_keys = []
        self.replaced_keys = []

        self.allow_reuse_overlays = True

    def main(self):
        if "install" in sys.argv:
            self.allow_reuse_overlays = False
            self.generate_modified_keymap_data()
            name, contents_str = generate_keyboard_layout_file_str(get_current_keyboard_layout_id(), self.created_keys, self.replaced_keys)
            install_keyboard_layout_file(contents_str, name)
            add_layout_to_rules_xml_file(get_current_keyboard_layout_id(), f"{get_current_keyboard_layout_id()}_hrc")
            print("In order to activate the generated layout, go to your Keyboard Settings GUI and search for 'hrc'.")
            sys.exit(0)

        if "nosleep" not in sys.argv:
            time.sleep(5)

        if f"{get_current_keyboard_layout_id()}_hrc" in os.listdir(get_symbols_install_dir()):
            os.system(f"setxkbmap {get_current_keyboard_layout_id()}_hrc")
        
        self.configure_keymap()

        try:
            s = socket.socket()
            s.bind(("localhost", 24679))
            s.listen(1)

            for overlay in self.overlays:
                overlay.start_hooking_keyboard()

            while True:
                try:
                    s.accept()
                    time.sleep(5)
                    self.load_keymap_file(self.keymap_file)
                except KeyboardInterrupt:
                    for overlay in self.overlays:
                        overlay.stop_hooking_keyboard()
                    break
        except OSError as e:
            print(e, ". Another instance of this program is already running. Kill previous instance and "
                     "restart the program if you want command overlays to work correctly.")

    def store_used_key_labels(self):
        file_data = ""
        key_labels = []
        # remove double elements
        for key_label in self.used_key_labels:
            if key_label not in key_labels:
                key_labels.append(key_label)
        self.used_key_labels = key_labels
        for key_label in self.used_key_labels:
            file_data += "\n" + key_label
        with open(self.generated_key_labels_file, "w") as f:
            f.write(file_data)

    def restore_used_key_labels(self):
        if os.path.isfile(self.generated_key_labels_file):
            codes = read_file(self.generated_key_labels_file).split("\n")
            while '' in codes:
                codes.remove('')
            return codes
        else:
            return []

    def get_interpret_section(self, stroke):
        re_stroke = stroke.replace("+", "\\+").replace("(", "\\(").replace(")", "\\)")
        groups = re.search(r"interpret *" + re_stroke + r" *\{[^}]*\}([ \n])*;", self.keymap_data)
        if groups is None:
            return None
        interpret_section = groups.group(0)
        return interpret_section

    def get_key_label(self, key_code):
        key_codes = self.get_xkb_keycodes_section()
        key_code_search = re.search(r"<.{2,6}> *= *" + str(key_code) + r" *;", key_codes).group(0)
        key_label = key_code_search.split("=")[0].strip(' ')[1:-1]
        return key_label

    def get_key_code(self, key_label):
        key_codes = self.get_xkb_keycodes_section()
        key_label_search = re.search(r"<" + str(key_label) + "> *= *[0-9]{1,10};", key_codes).group(0)
        key_code = key_label_search.split("=")[1].strip(' ')[:-1]  # cut ';'
        return key_code

    def get_xkb_keycodes_section(self):
        return re.search(r"xkb_keycodes *\".*\" *\{[^}]*\}", self.keymap_data).group(0)

    def get_xkb_symbols_section(self):
        return re.search(r"xkb_symbols *\".*\" *\{([^{]+(name|key)[^{]+\{[^}]+\};)*", self.keymap_data).group(0)

    def get_xkb_symbols_section_name(self):
        xkb_symbols_str = self.get_xkb_symbols_section()
        name = xkb_symbols_str.split("xkb_symbols")[1].split("{")[0]
        name = name.strip(" ").strip("\t").strip('"')
        return name

    def get_keysym_section(self, key_label):
        key_label = key_label.upper()
        return re.search(r"key <" + key_label + r"> \{[^}]*\};", self.keymap_data).group(0)
    
    def has_keysym_section(self, key_label):
        return re.search(r"key <" + key_label + r"> \{[^}]*\};", self.keymap_data) is not None

    def get_unused_key_labels(self):
        all_codes = self.get_key_labels()
        codes = []
        xkb_symbols_section = self.get_xkb_symbols_section()
        for key_label in all_codes:
            if key_label not in xkb_symbols_section:
                codes.append(key_label)
        return codes

    def get_key_labels(self):
        codes = []
        for i in range(9, 255):
            try:
                key_label = self.get_key_label(i)
                codes.append(key_label)
            except AttributeError as e:
                pass
        return codes

    def has_overlay(self, key_label, overlay_num):
        old_key_def = self.get_keysym_section(key_label)
        if f"overlay{overlay_num}" in old_key_def:
            return True
        else:
            return False
    
    def get_overlay(self, key_label, overlay_num):
        key_def = self.get_keysym_section(key_label)
        if f"overlay{overlay_num}" not in key_def:
            return None
        overlay_key_label = key_def.split(f"overlay{overlay_num}")[1].split("=")[1].split("\n")[0]
        overlay_key_label = overlay_key_label.split("<")[1].split(">")[0]
        return overlay_key_label

    def add_overlay_key(self, key_label, overlay_key_label, num_overlay):
        try:
            old_key_def = new_key_def = self.get_keysym_section(key_label)
            if self.has_overlay(key_label, num_overlay):
                if self.get_overlay(key_label, num_overlay) == overlay_key_label:
                    print(f"{key_label} is already overlayed by {overlay_key_label}")
                    self.replaced_keys.append(old_key_def)
                    return True
                old_overlay = re.search(r",\n *overlay[0-9] *= *<.{2,6}>", old_key_def).group(0)
                new_key_def = new_key_def.replace(old_overlay, "")
            new_key_def = new_key_def.replace("}",
                                              ",   overlay" + str(num_overlay) + " = <" + overlay_key_label + "> \n}")
            self.replaced_keys.append(new_key_def)
            self.keymap_data = self.keymap_data.replace(old_key_def, new_key_def)
            print(f"overlayed {key_label} with {overlay_key_label}")
            return True
        except Exception as e:
            print(e)
            return False

    def remove_overlay_key_interpret(self, num_overlay):
        num_overlay = str(num_overlay)
        interpret_section = self.get_interpret_section("Overlay%s_Enable+AnyOfOrNone(all)" % num_overlay)
        if interpret_section is not None:
            self.keymap_data = self.keymap_data.replace(interpret_section, "")

    def set_overlay_enable_key(self, key_label, num_overlay):
        # set up modifier key
        old_keysym_section = self.get_keysym_section(key_label)
        keysym = read_file("assets/overlay_enable_keysym").replace("####", key_label).replace("$$$$", str(num_overlay))
        self.replaced_keys.append(keysym)
        self.keymap_data = self.keymap_data.replace(old_keysym_section, keysym)

    def create_keysym_section(self, key_label, keys_string):
        try:
            new_key_data = "\n    key <" + key_label + "> {[" + keys_string + "]};"
            xkb_symbols_section = old_xkb_symbols_section = self.get_xkb_symbols_section()
            xkb_symbols_section += new_key_data
            self.keymap_data = self.keymap_data.replace(old_xkb_symbols_section, xkb_symbols_section)
            self.used_key_labels.append(key_label)
            self.created_keys.append(new_key_data)
            return True
        except AttributeError as e:
            print(e)
            return False

    def create_keysym_sections(self, mapping_data, overlay_index):
        failed = False
        for mapping in mapping_data:
            if "mapped_keysym" in mapping:
                key_label = self.get_key_label(mapping["key_code"])
                overlay_key_label = self.create_or_reuse_overlay(key_label, mapping["mapped_keysym"], overlay_index)
                if overlay_key_label is None:
                    print(f"Failed to map {key_label} to {mapping['mapped_keysym']}")
                    failed = True
        if failed and len(self.get_unused_key_labels()) == 0:
            print("============================================================")
            print("NO FREE KEY LABELS AVAILABLE FOR SPECIAL MAPPINGS!!! ")
            print("please try switching layouts using settings or log back in again if that is not helping")
            print("if this problem persists, you may also have exceeded the number of available key labels")
            print("============================================================")
        return not failed

    def map_overlay_keys(self, mapping_data, num_overlay):
        # add overlays to keys
        for mapping in mapping_data:
            if "mapped_key_label" in mapping:
                code = mapping["key_code"]
                overlay_key_label = mapping["mapped_key_label"]
                key_label = self.get_key_label(code)
                self.add_overlay_key(key_label, overlay_key_label, num_overlay)
    
    def create_or_reuse_overlay(self, key_label, key_sym, overlay_index):
        overlay_key_label = self.get_overlay(key_label, overlay_index)
        if not self.allow_reuse_overlays:
            overlay_key_label = None
        # TODO improve this check
        if overlay_key_label is not None and self.has_keysym_section(overlay_key_label):
            if key_sym not in self.get_keysym_section(overlay_key_label):
                print(f"Found active overlay for {key_label}: {overlay_key_label}, but {overlay_key_label} does not produce {key_sym}.")
                print("  That means it can not be re-used.")
                overlay_key_label = None
        reusing = keysym_created = False
        if overlay_key_label is None:
            overlay_key_label = self.get_unused_key_labels()[-1]
            self.create_keysym_section(overlay_key_label, key_sym)
        else:
            reusing = True
            if not self.has_keysym_section(overlay_key_label):
                keysym_created = True
                self.create_keysym_section(overlay_key_label, key_sym)
        if not self.add_overlay_key(key_label, overlay_key_label, overlay_index):
            print(f"Failed to overlay {key_label} with {overlay_key_label}")
            return None
        if reusing:
            print(f"    Re-used existing mapping of {key_label} to {overlay_key_label} to generate {key_sym}.")
            if keysym_created:
                print(f"    Re-created keysym section for {overlay_key_label} to generate {key_sym}.")
        if overlay_key_label is not None:
            if overlay_key_label in self.get_unused_key_labels():
                self.get_unused_key_labels().remove(overlay_key_label)
        return overlay_key_label

    def map_commands(self, mapping_data, overlay):
        for mapping in mapping_data:
            if "mapped_sequences" in mapping:
                sequences = mapping["mapped_sequences"]
                key_label = self.get_key_label(mapping["key_code"])
                overlay_key_label = self.create_or_reuse_overlay(key_label, "NoSymbol", overlay.index)
                if overlay_key_label is None:
                    continue
                if overlay_key_label is not None:
                    overlay.add_command_mapping(self.get_key_code(overlay_key_label), sequences)
                else:
                    print(f"Could not find an overlay key to create for {key_label}")
    
    def generate_modified_keymap_data(self):
        self.__init__()
        self.capture_keymap(self.keymap_file)

        # remove key_labels added during last execution
        while len(self.used_key_labels) > 0:
            previously_used_key_label = self.used_key_labels.pop()
            try:
                self.keymap_data = self.keymap_data.replace(self.get_keysym_section(previously_used_key_label), "")
            except AttributeError as e:
                pass

        self.overlays = []
        for num_overlay in [1, 2]:
            overlay_id = "overlay" + str(num_overlay)
            if self.config[overlay_id]["key"] != "disabled":
                overlay_key_label = self.config[overlay_id]["key"]
                overlay_key_code = self.get_key_code(overlay_key_label)
                overlay_key_mode = self.config[overlay_id]["mode"]
                mapping_data = self.config[overlay_id]["mapping"]
                self.create_keysym_sections(mapping_data, num_overlay)
                self.set_overlay_enable_key(overlay_key_label, num_overlay)
                self.map_overlay_keys(mapping_data, num_overlay)

                global xlib_support
                if xlib_support:
                    overlay = CommandOverlay(num_overlay, overlay_key_code, overlay_key_mode)
                    self.map_commands(mapping_data, overlay)
                    self.overlays.append(overlay)

        return self.keymap_data

    def configure_keymap(self):
        self.generate_modified_keymap_data()

        with open(self.keymap_file, "w") as f:
            f.write(self.keymap_data)
        self.load_keymap_file(self.keymap_file)

    def capture_keymap(self, filename):
        os.system("xkbcomp -xkb $DISPLAY " + filename)
        self.keymap_data = read_file(filename)

    def load_keymap_file(self, filename):
        self.store_used_key_labels()
        print("Loading generated keymap with xkb...")
        output = os.popen("xkbcomp -xkb %s $DISPLAY" % filename).read()
        if "rror" not in output:
            print("Successfully loaded keymap.")
            os.remove(filename)
        else:
            print("Error while loading keymap.")
        print("INFO: still " + str(len(self.get_unused_key_labels())) + " key_labels available for custom mappings.")


class CommandOverlay:
    def __init__(self, index, overlay_enable_key_code, overlay_enable_mode):
        self.command_mapping = {}
        self.index = index

        self.__available_modifiers = {
            "None": 0,
            "Shift": Xlib.X.ShiftMask,
            "Control": Xlib.X.ControlMask,
            "Alt": Xlib.X.Mod1Mask,
        }

        self.__available_modifier_state_mask = sum(self.__available_modifiers.values())

        self.key_code = int(overlay_enable_key_code)
        if overlay_enable_mode == "hold":
            self.on_overlay_key = self.hold_overlay_key
        elif overlay_enable_mode == "toggle":
            self.on_overlay_key = self.toggle_overlay_key

        self.key_faker = None

        self.overlay_active = False

        self.hookManager = pyxhook.HookManager()
        self.hookManager.HookKeyboard()
        self.hookManager.KeyDown = self.handle_key_event
        self.hookManager.KeyUp = self.handle_key_event

    def start_hooking_keyboard(self):
        self.hookManager.start()
        self.key_faker = KeyFaker()

    def stop_hooking_keyboard(self):
        self.hookManager.cancel()

    def add_command_mapping(self, key_code, sequences):
        key_code = int(key_code)
        self.__adjust_command_sequences_prop_names(sequences)
        self.command_mapping[key_code] = self.__create_combined_modifiers_commands_map(sequences)

    def handle_key_event(self, event):
        if event.ScanCode == self.key_code:
            self.on_overlay_key(event.MessageName)
        else:
            if self.overlay_active and event.ScanCode in self.command_mapping:
                # restrict the state to only the modifiers available here
                restricted_state = event.XLibEvent.state & self.__available_modifier_state_mask
                command_sequences = self.command_mapping[event.ScanCode][restricted_state]
                # which modifiers triggered the command?
                captured_state = command_sequences["__trigger_modifier_state__"]
                # which modifiers are pressed additionally that we must continue to hold?
                forwarded_state = restricted_state - captured_state
                sequence = command_sequences[event.MessageName]
                self.execute_command_sequence(sequence, current_modifier_state=forwarded_state)

    def __adjust_command_sequences_prop_names(self, command_sequences):
        if "down" in command_sequences:
            command_sequences["key down"] = command_sequences["down"]
        if "up" in command_sequences:
            command_sequences["key up"] = command_sequences["up"]
        if "key down" not in command_sequences:
            command_sequences["key down"] = []
        if "key up" not in command_sequences:
            command_sequences["key up"] = []

    def __create_combined_modifiers_commands_map(self, command_sequences):
        # all possible modifier states, thus any combinations of available modifiers summed up
        all_possible_combined_states = [0]  # 0 = state for no modifiers

        # A map that maps any modifier combination to a command.
        # A command is assigned to a modifier combination, iff its trigger state ANDs (&) with the combination and
        # at the same time no command is defined for a larger combination that fits the combination
        all_possible_states_command_map = {}

        for i in range(0, len(self.__available_modifiers) + 1):
            # get all modifier combinations for length i (unfortunately includes different ordering as well)
            combinations_length_i = itertools.combinations(self.__available_modifiers.values(), i)
            # sum up items of each combination
            states_length_i = [sum(combination) for combination in combinations_length_i]
            # eliminate duplicates
            states_length_i = list(set(states_length_i))
            all_possible_combined_states += states_length_i

        command_sequences["__trigger_modifier_state__"] = 0

        for state_combination in all_possible_combined_states:
            all_possible_states_command_map[state_combination] = command_sequences

        if "if_modifiers" in command_sequences:
            state_command_list = []
            state_command_map = {}

            for modifiers, command in command_sequences["if_modifiers"].items():
                state = self.__parse_modifier_state(modifiers)
                state_command_list.append(state)
                command["__trigger_modifier_state__"] = state
                self.__adjust_command_sequences_prop_names(command)
                state_command_map[state] = command

            state_command_list.sort()

            for state in all_possible_combined_states:
                command = None
                for trigger_state in state_command_list:
                    if state & trigger_state > 0:
                        command = state_command_map[trigger_state]
                if command:
                    all_possible_states_command_map[state] = command

        return all_possible_states_command_map

    def __get_active_modifiers(self, modifier_state):
        modifiers = []
        for modifier, state in self.__available_modifiers:
            if modifier_state & state:
                modifiers.append(modifier)
        return modifiers

    def __parse_modifier_state(self, modifiers):
        parsed_state = 0
        modifiers_list = []
        if isinstance(modifiers, list):
            modifiers_list = modifiers
        # when the user gave us a plus-separated string with modifiers, split them to obtain a list
        if isinstance(modifiers, str):
            modifiers_list = modifiers.split("+")
        # remove space before and after each modifier
        modifiers_list = [mod.strip(" ") for mod in modifiers_list]
        for modifier, state in self.__available_modifiers.items():
            if modifier in modifiers_list:
                parsed_state = parsed_state | state
        return parsed_state

    def __get_user_added_modifiers(self, command):
        if "modifiers" in command:
            return self.__parse_modifier_state(command["modifiers"])
        else:
            return 0

    def execute_command_sequence(self, sequence, current_modifier_state=0):
        for command in sequence:
            try:
                if isinstance(command, str):
                    os.system(command)
                elif isinstance(command, dict):
                    times = 1
                    if "times" in command:
                        times = command["times"]
                    text = command["text"] if "text" in command else None
                    key = command["key"] if "key" in command else None
                    key_code = command["key_code"] if "key_code" in command else None
                    # OR the user-added modifiers with the current modifier state,
                    # so that modifiers that are currently hold by the user do not get lost
                    modifier_state = self.__get_user_added_modifiers(command) | current_modifier_state
                    for i in range(times):
                        if text:
                            self.key_faker.type_text(text)
                        elif key:
                            self.key_faker.send_key(key, state=modifier_state)
                        elif key_code:
                            self.key_faker.send_key_code(key_code, state=modifier_state)
            except Exception as e:
                print("Error executing user defined command: ", e)

    def toggle_overlay_key(self, event_message):
        if event_message == "key down":
            self.overlay_active = not self.overlay_active

    def hold_overlay_key(self, event_message):
        self.overlay_active = (event_message == "key down")


class KeyFaker:
    special_character_mapping = {
        '@': 'at', '`': 'grave', '\t': 'Tab', '|': 'bar', '\n': 'Return', '\r': 'Return',
        '~': 'asciitilde',
        '{': 'braceleft', '[': 'bracketleft', ']': 'bracketright', '\\': 'backslash',
        '_': 'underscore',
        '^': 'asciicircum', '!': 'exclam', ' ': 'space', '#': 'numbersign', '"': 'quotedbl',
        '%': 'percent', '$': 'dollar',
        "'": 'apostrophe', '&': 'ampersand', ')': 'parenright', '(': 'parenleft', '+': 'plus',
        '*': 'asterisk',
        '-': 'minus', ',': 'comma', '/': 'slash', '.': 'period', '\\e': 'Escape',
        '}': 'braceright', ';': 'semicolon',
        ':': 'colon', '=': 'equal', '<': 'less', '?': 'question', '>': 'greater'
    }

    def __init__(self):
        self.display = Xlib.display.Display()
        self.root = self.display.screen().root

    def __current_window(self):
        return self.display.get_input_focus()._data["focus"]

    def __char_to_key_code(self, char):
        key_symbol = Xlib.XK.string_to_keysym(char)
        if key_symbol == 0:
            key_symbol = Xlib.XK.string_to_keysym(self.special_character_mapping[char])
        return self.display.keysym_to_keycode(key_symbol)

    def send_key(self, key_string, state=0):
        self.send_key_code(self.display.keysym_to_keycode(Xlib.XK.string_to_keysym(key_string)), state=state)
        self.__key_release(key_code=0)

    def type_text(self, text):
        for char in text:
            if char.isupper() or "{}<>()_\"?~!$%^&*+|:@#".find(char) >= 0:
                state = Xlib.X.ShiftMask
            else:
                state = 0
            self.__send_character(char, state=state)
        self.__key_release(key_code=0)
        self.display.sync()

    def send_key_code(self, key_code, state=0):
        window = self.__current_window()
        self.__key_press(window=window, key_code=key_code, state=state)
        self.__key_release(window=window, key_code=key_code, state=state)

    def __send_character(self, character, state=0):
        key_code = self.__char_to_key_code(character)
        self.send_key_code(key_code, state=state)

    def __key_press(self, window=None, key=None, key_code=None, state=0):
        if window is None:
            window = self.__current_window()
        if key_code is None:
            key_code = self.__char_to_key_code(key)
        key_press_event = Xlib.protocol.event.KeyPress(
            time=int(time.time()),
            root=self.root,
            window=window,
            same_screen=0, child=Xlib.X.NONE,
            root_x=0, root_y=0, event_x=0, event_y=0,
            state=state,
            detail=key_code
        )
        window.send_event(key_press_event, propagate=True)

    def __key_release(self, window=None, key=None, key_code=None, state=0):
        if window is None:
            window = self.__current_window()
        if key_code is None:
            key_code = self.__char_to_key_code(key)
        key_release_event = Xlib.protocol.event.KeyRelease(
            time=int(time.time()),
            root=self.root,
            window=window,
            same_screen=0, child=Xlib.X.NONE,
            root_x=0, root_y=0, event_x=0, event_y=0,
            state=state,
            detail=key_code
        )
        window.send_event(key_release_event, propagate=True)


if __name__ == "__main__":
    mapper = Mapper()
    mapper.main()
