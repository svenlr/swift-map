# Swift Map - Home Row Computing Keyboard Overlay

Arrow keys and other navigation keys accessible while staying on the home row!<br>
How? Specify a key, disable its normal behaviour and use it as an activator for
another key layer on your keyboard (this program comes with a default configuration using CapsLock).<br>
You can use the layout on both **Linux and Windows** without administrator rights!

## Installation on Linux

- (**optional**) If you like to use command and string injection, please install python-xlib<br>
  ```bash
  sudo apt install python3-xlib
  # or
  pip install XLib
  ```

- clone this repository.
  ```bash
  git clone https://github.com/svenlr/swift-map.git
  ```

- change working directory to the installation directory
  ```bash
  cd swift-map
  ```

- make scripts executable
  ```bash
  chmod +x mainloop.py
  ```

- test it
  ```bash
  ./mainloop.py nosleep
  ```
  To test it, now open an editor and try pressing ijkl with and without CAPS held down.

- Add it to start up (tested on Ubuntu 18.04 - 22.04):
  1. Go to the launcher and open the program 'Startup Applications'.
  2. Click on 'Add'.
  3. Enter some name, such as Keyboard Remap.
  4. Click on 'Browse'.
  5. Navigate to 'mainloop.py'.

- If you have sudo rights, you can permanently install the layout to your layout switcher. This also prevents the keyboard layout from breaking when resuming from sleep or attaching USB devices, etc...
  (Please be aware that the **installation modifies system config files** and the authors take no responsibilities for that.)
  ```
  ./mainloop.py install
  
  # Note that the installation alone does not handle snippet or command mappings, running the program on start-up is still required for that.
  ```

## Configuration File (Linux only)

The new key layer can be customized using a JSON configuration file on Linux (`config.json`).
A default configuration file is already included. Add more mappings and functionality by editing it.

- It is recommended to edit the JSON configuration file with an IDE/Editor that supports JSON, for example any JavaScript IDE/Editor should work. PyCharm works, too.
- You can use the `xev` command line tool to obtain the `"key_code"` for the keys that you want to remap.
`xev` also prints the key symbols (`mapped_keysym`) such as `braceleft`. For `xev` to work, you need to have focus (click on) the box window that appears after you started `xev`.

Choosing a mapping type:
- Example: If you want to make caps + r act like a Esc key use Cross Mapping ("mapped_key_label"). 
_Cross Mapping_ should be used when the target key (in this case Esc) is available without modifiers on your keyboard. 
- Example: If you want to assign symbols like `/` `(` `)` `=` to keys then use Key Symbol Mapping ("mapped_keysym").
_Key Symbol Mapping_ should be used when the target symbol (in this case `/` `(` `)` `=`) is **not** available without modifiers on your keyboard. 

### Cross Mapping (`mapped_key_label`)

Simulate pressing another key on your keyboard with the overlay. You can create as many Cross Mappings as you like. This method should be used if the target key - the one that you want to produce - is available somewhere on your keyboard without modifiers.

**Example:** We want to map Caps+o to PageDown.
(i.e., for every application, it will look as if you pressed the PageDown arrow key when you press Caps+o).
1. In order to find the key code for o, you type `xev` in command line, focus the appearing window and then press o. The key code is printed in the terminal, usually 32.
2. With `xev`, find the key code for the PageDown - usually 117.
3. Now, find the key label: `cat /usr/share/X11/xkb/keycodes/evdev | grep " 117;"` , which prints ```<PGDN> = 117;```

Here is the resulting JSON for remapping Caps+o to the PageDown key (PGDN):
```json
...
{
  "key_code": 32,
  "mapped_key_label": "PGDN"
},
...
```

### Key Symbol Mapping (`mapped_keysym`)

Use this if you want to generate a key that is not available on your keyboard without additional modifiers or not available at all.
**Example:** We want to map Caps+7 to the left brace `{`.
1. Again, in order to find the key code for 7, we use `xev`, which gives us 16 in the example.
2. Then, we want to find the key symbol (keysym) for the left brace `{`. In order to do that, just open `xev` and type the desired target key `{` using the necessary modifiers. Along with the key code, `xev` prints `braceleft`, which is our keysym.

Here is the resulting JSON for remapping Caps+7 to the left brace `{`.
```json
...
{
  "key_code": 16,
  "mapped_keysym": "braceleft"
},
...
```

Note that for the moment, the number of mappings of this kind is usually limited by about 10.

### Command and String Mapping

This requires the installation of `python-xlib`.
Map a key code to a set of commands, also including shell commands.
Define two sequences of commands, one for key up and one for key down.
A command can be a string (evaluated as shell command), or an object in JSON notation.
The following example can also be found in the default configuration file and allows us to make german quotes in LaTeX with only two key strokes.

```json
...
{
  "key_code": 11,
  "mapped_sequences": {
    "down": [
      {"text": "\\glqq{} \\grqq{}"},
      {"key": "Left", "times": 7}
    ]
  }
},
...
```

Note that for the moment, the number of mappings of this kind is usually limited by about 10.

## Usage on Windows

At the moment, I just recreated the default layout using a forked AutoHotKey script as a suggestion for the usage on Windows.

- install [AutoHotKey](https://autohotkey.com/download/) - or use the [zip version](https://autohotkey.com/download/ahk.zip) if you don't have administrator rights on the system
- download the [AutoHotKey CapsLock Remapping .ahk Script (DE layout)](https://gist.github.com/svenlr/2e09166ae6b70f0fcf8c897b7e7d4be8) (**it will be downloaded UTF-8 encoded and must be converted to ANSI manually!** Can be done using e.g. Notepad++ Portable)
- place a batch script with the following content in the user autostart folder (%appdata%\Microsoft\Windows\Start Menu\Programs\Startup)

```bat
C:\path\to\autohotkey.exe C:\path\to\capslock_remapping.ahk
```

## Thanks
- [arensonzz](https://github.com/arensonzz) for writing documentation.
