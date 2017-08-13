# Swift Map - Home Row Computing Keyboard Overlay

Arrow keys and other navigation keys accessible while staying on the home row!<br>
How? Specify a key, disable its normal behaviour and use it as an activator for
another key layer on your keyboard (this program comes with a default configuration using CapsLock).<br>
You can use the layout on both **Linux and Windows** without administrator rights!

## Installation on Linux

- (**optional**) If you like to use command and string injection, please install python-xlib<br>
  ```bash
  sudo apt install python-xlib
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
  ./mainloop.py &
  ```
  now open an editor and try pressing ijkl with and without caps held down.

- add it to start up (tested on Ubuntu based systems)<br>
  Go to the launcher and open the program 'Startup Applications'.<br>Click on 'Add'.<br>Enter some name.<br>Click on 'Browse'.<br>Navigate to 'mainloop.py'.

<!-- - add it to resume directory so the overlays still work after resume
<pre>$ sudo cp resume.py /etc/pm/sleep.d/</pre> -->

## Usage on Windows

At the moment, I just recreated the default layout using a forked AutoHotKey script as a suggestion for the usage on Windows.

- install [AutoHotKey](https://autohotkey.com/download/) - or use the [zip version](https://autohotkey.com/download/ahk.zip) if you don't have administrator rights on the system
- download the [AutoHotKey CapsLock Remapping .ahk Script (DE layout)](https://gist.github.com/svenlr/2e09166ae6b70f0fcf8c897b7e7d4be8) (**it will be downloaded UTF-8 encoded and must be converted to ANSI manually!** Can be done using e.g. Notepad++ Portable)
- place a batch script with the following content in the user autostart folder (%appdata%\Microsoft\Windows\Start Menu\Programs\Startup)

```bat
C:\path\to\autohotkey.exe C:\path\to\capslock_remapping.ahk
```

## Configuration File (Linux only)

The new key layer can be customized using a JSON configuration file on Linux.
A default configuration file is already included. Add more mappings and functionality by editing it.
There are three types of mapping:

### Cross Mapping

Map a key code directly to another key code.
Example: In the default overlay, i is mapped directly to your Up key, for every application,
it will look as if you pressed the Up arrow key.

```json
...
{
  "key_code": 32,
  "mapped_key_label": "PGDN"
},
...
```

### Key Symbol Mapping

Map a key code directly to another key code generated by the program. Specify a key symbol,
e.g. 'braceleft' and the program uses a previously unused key code to create a new 'virtual key'.
Then it creates a 'Cross Mapping'.

```json
...
{
  "key_code": 16,
  "mapped_keysym": "braceleft"
},
...
```

Note that this method requires unused key codes in your keymap, which are limited.

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

Note that this method requires unused key codes in your keymap, which are limited.
This will be improved in the future.
