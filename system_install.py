"""
The MIT License (MIT)

Copyright (c) 2024 Sven Langner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import xml.etree.ElementTree as etree
import io


def generate_keyboard_layout_file_str(
    based_of: str, new_key_sections, replaced_key_sections
):
    contents = ""
    contents += "default partial alphanumeric_keys modifier_keys keypad_keys\n"
    includes = ""
    includes += f'\n    include "{based_of}(basic)"'
    new_name = based_of + "_hrc"
    contents += f'xkb_symbols "{new_name}" ' + "{"
    contents += includes
    contents += "\n"
    for key_section in new_key_sections:
        contents += key_section
    for key_section in replaced_key_sections:
        contents += "\n    replace " + key_section.replace("};", "    };")
    contents += "\n};"

    return new_name, contents


def get_xkb_base_dir():
    return "/usr/share/X11/xkb/"


def get_symbols_install_dir():
    return f"{get_xkb_base_dir()}symbols/"


def get_rules_install_dir():
    return f"{get_xkb_base_dir()}rules/"


def install_keyboard_layout_file(contents, new_name):
    with open("/tmp/new_xkb_map", "w+") as f:
        f.write(contents)
    print("")
    print(contents)
    print("")
    cmd = f"sudo -k cp /tmp/new_xkb_map {get_symbols_install_dir()}{new_name}"
    print(f"Enter sudo pw to copy layout to system:\n{cmd}")
    os.system(cmd)


def add_layout_to_rules_xml_file(old_name, new_name):
    # TODO it is not always evdev?
    path = os.path.join(get_rules_install_dir(), "evdev.xml")
    xml_str = open(path).read()
    # make sure there is only one occurence of </layoutList> closing tag
    assert len(xml_str.split("</layoutList>")) == 2
    root = etree.parse(open(path)).getroot()
    layoutList = root.find("layoutList")
    layouts = layoutList.findall("layout")
    old_desc_short = None
    old_desc = None
    country_list = None
    language_list = None
    for layout in layouts:
        configItem = layout.find("configItem")
        name = configItem.find("name").text
        if name == old_name:
            old_desc = configItem.find("description").text
            old_desc_short = configItem.find("shortDescription").text
            country_list = configItem.find("countryList")
            language_list = configItem.find("languageList")
        if name == new_name:
            print(f"Already installed in {path}: {new_name}!  (Edit file manually to remove {new_name} and trigger re-installation)")
            return
    if old_desc is None:
        raise RuntimeError(
            f"could not find layout with name {old_name} to base description of new layout on"
        )
    country_list = etree.tostring(country_list).decode("utf-8").strip(" ").strip("\n") if country_list else ""
    language_list = etree.tostring(language_list).decode("utf-8").strip(" ").strip("\n") if language_list else ""
    new_layout_str = f"""
    <layout>
      <configItem>
        <name>{new_name}</name>
        <shortDescription>{old_desc_short}</shortDescription>
        <description>{old_desc} (hrc)</description>
        {country_list}
        {language_list}        
      </configItem>
    </layout>
    """
    print(f"Adding the following to {path}")
    print(new_layout_str)
    part_before, part_after = xml_str.split("</layoutList>")
    new_full_xml = part_before + new_layout_str + "\n  </layoutList>" + part_after
    try:
        # sanity check: can we still parse after adding the layout?
        etree.parse(io.StringIO(new_full_xml))
    except etree.ParseError:
        raise RuntimeError("Bug in XML generation. Could not be parsed after adding new layout.")
    
    with open("/tmp/new_evdev.xml", "w+") as f:
        f.write(new_full_xml)
    cmd = f"sudo -k cp /tmp/new_evdev.xml {path}"
    print(f"Enter sudo pw to copy new evdev.xml to system:\n{cmd}")
    os.system(cmd)


def get_current_keyboard_layout_id():
    return (
        os.popen("setxkbmap -query")
        .read()
        .split("layout:")[1]
        .replace("\t", "")
        .replace(" ", "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("_hrc", "")
    ).split(",")[0]
