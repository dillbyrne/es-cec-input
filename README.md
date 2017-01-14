# es-cec-input
TV CEC remote control for Emulation Station (included in RetroPie)

# Features

* It will automatically map your retroarch keyboard config to the remote control buttons. ( See Supported Keyboard Keys Below )

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
It depends on the `cec-utils` package and also the `python-uinput` package which contains the library and the udev rules at 
`/etc/udev/rules.d/40-uinput.rules`.  

Both `cec-utils` and `python-uinput` are in the repositories.

The `40-uinput.rules` file should look like the following

```
ACTION=="add|change", KERNEL=="event[0-9]*", ENV{ID_VENDOR_ID}=="012a", ENV{ID_MODEL_ID}=="034b",
ENV{ID_INPUT_KEYBOARD}="1", ENV{ID_INPUT_TABLET}="1"SUBSYSTEM=="input", ATTRS{name}=="python-uinput",
ENV{ID_INPUT_KEYBOARD}="1"KERNEL=="uinput", MODE:="0666" 
```

# Run the code as a non root user
You must first create the uinput group 

`sudo addgroup uinput`

Then add the pi user to the uinput group

`sudo adduser pi uinput`


# Testing before autostart

**Note: It was developed and tested on a pi3 with Retropie 4.1 with kodi installed in 
the ports section of retropie**

To make sure it will work you should run the script
as a non root user.

First make the script executable (assuming your in the same directory as the file)

`chmod u+x es-cec-input.py`

then run it with

`./es-cec-input.py`

If you see no output then you can try your TV remote with the buttons
in the Button section above. If it works then proceed to the next section

If you see output it will exit and tell you the key which is unsupported and 
a list of the supported keys.

Ensure all your keys are supported and try again until you get no output.

# Autostart on boot
To start on boot, add to user's crontab. 

`crontab -e`

Add the line,

`@reboot nohup ./home/pi/PATH/TO/THE/SCRIPT/es-cec-input.py`


# Supported Keyboard Keys

**Note: You must set up your keyboard in Emulation Station first or the script will not work**

As keys need to be mapped from retroarch.cfg supported keys to corresponding uinput supported keys not all the keys are available. However most are supported, as seen below


Letters ("a" to "z"), left, right, up, down, enter, kp_enter, tab, insert, del, end, home, rshift, shift, ctrl, alt, space, escape, kp_plus, kp_minus, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12,  num0, num1, num2, num3, num4, num5, num6, num7, num8, num9, pageup, pagedown, keypad0, keypad1, keypad2, keypad3, keypad4, keypad5, keypad6, keypad7, keypad8, keypad9, period, capslock, numlock, backspace, scroll_lock, backquote, pause, quote, comma, minus, slash, semicolon, equals, backslash, kp_period, kp_equals, rctrl, ralt

(where "kp_"# is for keypad keys)
