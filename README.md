# es-cec-input
TV CEC remote control support for Emulation Station (included in RetroPie)

# Features

* It will automatically map your retroarch keyboard config to the remote control buttons. Ensure you pick a key for all available options ( See Supported Keyboard Keys Below )

* It will not act on remote button presses when kodi or retroarch is running and will act as soon as ES returns or starts.



# Buttons

ES       <->         TV Remote

A        <->        SELECT or RED

B        <->        EXIT or GREEN

UP       <->        UP

DOWN     <->        DOWN

LEFT     <->        LEFT

RIGHT    <->        RIGHT

START    <->        FAST FORWARD or BLUE

SELECT   <->        REWIND OR YELLOW

# Dependencies

**Note: You must setup a keyboard through the Emulationstation GUI prior to doing any of the below!**

It depends on the `cec-utils` package and also the `python-uinput` package which contains the library and the udev rules at 
`/etc/udev/rules.d/40-uinput.rules`.  

Both `cec-utils` and `python-uinput` are in the repositories.
and can be installed with:
```
sudo pip install python-uinput
sudo apt-get install cec-utils
```

if python-uinput gives you a `bist-wheel` error, then do the following:
```
sudo pip uninstall python-uinput
sudo pip install wheel
sudo pip install python-uinput
```

The `40-uinput.rules` file should look like the following

```
ACTION=="add|change", KERNEL=="event[0-9]*", ENV{ID_VENDOR_ID}=="012a", ENV{ID_MODEL_ID}=="034b",
ENV{ID_INPUT_KEYBOARD}="1", ENV{ID_INPUT_TABLET}="1"SUBSYSTEM=="input", ATTRS{name}=="python-uinput",
ENV{ID_INPUT_KEYBOARD}="1"KERNEL=="uinput", MODE:="0666" 
```
If not modify/create it with:
```
sudo nano /etc/udev/rules.d/40-uinput.rules
```
and add the code from above.

# To run the code as a non root user
You must first create the uinput group 

`sudo addgroup uinput`

Then add the pi user to the uinput group

`sudo adduser pi uinput`


# Testing before autostart

**Note: It was developed and tested on a pi3 with Retropie 4.4.12 with kodi 18.2 installed in 
the ports section of retropie**

To make sure it will work you should run the script
as a non root user.

First download the code and make the script executable (assuming your in the same directory as the file)
```
wget https://raw.githubusercontent.com/MacGyverr/es-cec-input/master/es-cec-input.py
sudo chmod ugo+rwx es-cec-input.py
```

then run it with

`./es-cec-input.py`

If you see no output then you can try your TV remote with the buttons
in the Button section above. If it works then proceed to the next section

If you see output it will exit and tell you the key which is unsupported and 
a list of the supported keys.

Ensure all your keys are supported and try again until you get no output.

# Autostart on boot
To start on boot, add to user's crontab. (notice it's not using sudo)

`crontab -e`

Add the line,

`@reboot nohup /home/pi/PATH/TO/THE/SCRIPT/es-cec-input.py`
which if you didn't switch to a different folder before downloading the script will be /home/pi/, so use the following:

`@reboot nohup /home/pi/es-cec-input.py`


# Supported Keyboard Keys

**Note: You must set up your keyboard in Emulation Station first (pick a key for all options!) or the script will not work**

As keys need to be mapped from retroarch.cfg supported keys to corresponding uinput supported keys not all the keys are available. However most are supported, as seen below


Letters ("a" to "z"), left, right, up, down, enter, kp_enter, tab, insert, del, end, home, rshift, shift, ctrl, alt, space, escape, kp_plus, kp_minus, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12,  num0, num1, num2, num3, num4, num5, num6, num7, num8, num9, pageup, pagedown, keypad0, keypad1, keypad2, keypad3, keypad4, keypad5, keypad6, keypad7, keypad8, keypad9, period, capslock, numlock, backspace, scroll_lock, backquote, pause, comma, minus, slash, semicolon, equals, backslash, kp_period, kp_equals, rctrl, ralt

(where "kp_"# is for keypad keys)

# FAQ
* The script is not working after exiting from kodi. This is due to a setting in kodi. [Solution](https://github.com/dillbyrne/es-cec-input/issues/2#issuecomment-281341050) (tested fine without but who knows)
* Using remote is not controlling menu but signal is being received (goes out of screensaver). Happens when keyboard was not configured as a controller. [Solution](https://github.com/dillbyrne/es-cec-input/issues/1#issuecomment-272633575)
