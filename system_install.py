from typing import List
import os

def generate_keyboard_layout_file_str(based_of: str, new_key_sections, replaced_key_sections):
    contents = ""
    contents += "default partial alphanumeric_keys modifier_keys keypad_keys\n"
    includes = ""
    new_name = ""
    for include_kb in based_of.split("_"):
        if include_kb.split("(")[0] in ["pc", "inet"]:
            continue
        if "(" not in include_kb:
            includes += f'\n    include "{include_kb}(basic)"'
        else:
            includes += f'\n    include "{include_kb}"'
        new_name += include_kb.split("(")[0] + "_"
    new_name += "hrc"
    contents += f'xkb_symbols "{new_name}" ' + "{"
    contents += includes
    contents += "\n"
    for key_section in new_key_sections:
        contents += key_section
    for key_section in replaced_key_sections:
        contents += "\n    replace " + key_section.replace("};", "    };")
    contents += "\n};"
    with open("/tmp/new_xkb_map", "w+") as f:
        f.write(contents)
    print(contents)
    cmd = f"sudo cp /tmp/new_xkb_map /usr/share/X11/xkb/symbols/{new_name}"
    print(cmd)
    os.system(cmd )
