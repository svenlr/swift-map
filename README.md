# Coding without jumping around on the keyboard and twisting your fingers? Yes.
This little program allows you to easily set up overlays for your xkb keyboard.<br>
Specify a key (by default Caps Lock), disable its normal behaviour and use it as an activator for
another key layer on your keyboard.<br>
This also allows usage of navigation keys such as Up, Down, Left and Right on the home row.

## Configuration File
- easily define your own mappings in a JSON-based configuration file
- usage explained in the file itself

## Installation
<!---
you will need xdotool for input manipulation<br>
(if you do not have superuser rights, you can also download it and compile it yourself)
<pre>sudo apt-get install xdotool python-xlib</pre>
-->

- clone this repository to a path_of_your_choice.
<pre>git clone https://github.com/soeiner/homerow-arrowkeys.git path_of_your_choice</pre>

- change working directory to the installation directory
<pre>cd path_of_your_choice</pre>

- make scripts executable
<pre>chmod +x mainloop.py resume.py</pre>

- test it
<pre><br>./mainloop.py &</pre>
now open an editor and try pressing some keys with and without caps held down.

- add it to start up (tested on Ubuntu based systems)<br>
Go to the launcher and open the program 'Startup Applications'.<br>Click on 'Add'.<br>Enter some name.<br>Click on 'Browse'.<br>Navigate to 'mainloop.py'.

<<<<<<< HEAD
- add it to after resume execution
<pre>sudo cp resume.py /etc/pm/sleep.d/</pre>
=======
- add it to resume directory so the overlays still work after resume
<pre>sudo cp resume.py /etc/pm/sleep.d/</pre>
>>>>>>> xkbcomp
