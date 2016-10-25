# System wide usable navigation keys on the home row
This python script turns the Caps Lock key into a 'modifier'.

## Behaviour while caps is hold down
- level 3 shift is activated (the same as pressing 'Alt Gr')
- i, j, k and l can be used as arrow keys
- h becomes Pos1, oe End, u PageUp, o PageDown

## Installation
- you will need xdotool for input manipulation<br>
(if you do not have superuser rights, you can also download it and compile it yourself)
<pre>sudo apt-get install xdotool</pre>

- clone this repository to a path_of_your_choice.
<pre>git clone https://github.com/soeiner/homerow-arrowkeys.git path_of_your_choice</pre>

- change working directory to the installation directory
<pre>cd path_of_your_choice</pre>

- make it executable
<pre>chmod +x mainloop.py resume.py</pre>

- test it
<pre><br>./mainloop.py &</pre>
now open an editor and try pressing some keys with and without caps held down.

- add it to start up (tested on Ubuntu based systems)<br>
Go to the launcher and open the program 'Startup Applications'.<br>Click on 'Add'.<br>Enter some name.<br>Click on 'Browse'.<br>Navigate to 'mainloop.py'.

- add it to after resume execution
<pre>sudo cp resume.py /etc/pm/sleep.d/</pre>