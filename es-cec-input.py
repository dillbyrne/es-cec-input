#!/usr/bin/env python

"""
Name: es-cec-input.py
Version: 1.5
Description: cec remote control for emulation station in retropie
Author: dillbyrne
Homepage: https://github.com/dillbyrne/es-cec-input
Licence: GPL3

It depends on python-uinput package which contains
the library and the udev rules at
/etc/udev/rules.d/40-uinput.rules

cec-utils also needs to be installed

to run the code as a non root user
sudo addgroup uinput
sudo adduser pi uinput

to start on boot, add to user crontab. crontab -e
@reboot hohup ./home/pi/RetroPie/scripts/es-cec-input.py
"""

# (remote control) es-cec -> game controller -> keyboard -> uinput
# es-cec -> game controller: user defined
# game controller -> keyboard: retroarch.cfg
# keyboard -> uinput: static(es-cec-input)

import subprocess
import threading
import uinput
import os
import sys
import time
import string
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


def get_keyboard_to_uinput_map():
    """Map ES supported keys to python-uinput keys"""
    return {
            'left': uinput.KEY_LEFT, 'right': uinput.KEY_RIGHT,
            'up': uinput.KEY_UP, 'down': uinput.KEY_DOWN,
            'enter': uinput.KEY_ENTER, 'kp_enter': uinput.KEY_KPENTER,
            'tab': uinput.KEY_TAB, 'insert': uinput.KEY_INSERT,
            'del': uinput.KEY_DELETE, 'end': uinput.KEY_END,
            'home': uinput.KEY_HOME, 'rshift': uinput.KEY_RIGHTSHIFT,
            'shift': uinput.KEY_LEFTSHIFT, 'rctrl': uinput.KEY_RIGHTCTRL,
            'ctrl': uinput.KEY_LEFTCTRL, 'ralt': uinput.KEY_RIGHTALT,
            'alt': uinput.KEY_LEFTALT, 'space': uinput.KEY_SPACE,
            'escape': uinput.KEY_ESC, 'kp_minus': uinput.KEY_KPMINUS,
            'kp_plus': uinput.KEY_KPPLUS, 'f1': uinput.KEY_F1,
            'f2': uinput.KEY_F2, 'f3': uinput.KEY_F3,
            'f4': uinput.KEY_F4, 'f5': uinput.KEY_F5,
            'f6': uinput.KEY_F6, 'f7': uinput.KEY_F7,
            'f8': uinput.KEY_F8, 'f9': uinput.KEY_F9,
            'f10': uinput.KEY_F10, 'f11': uinput.KEY_F11,
            'f12': uinput.KEY_F12, 'num1': uinput.KEY_1,
            'num2': uinput.KEY_2, 'num3': uinput.KEY_3,
            'num4': uinput.KEY_4, 'num5': uinput.KEY_5,
            'num6': uinput.KEY_6, 'num7': uinput.KEY_7,
            'num8': uinput.KEY_8, 'num9': uinput.KEY_9,
            'num0': uinput.KEY_0, 'pageup': uinput.KEY_PAGEUP,
            'pagedown': uinput.KEY_PAGEDOWN, 'keypad1': uinput.KEY_KP1,
            'keypad2': uinput.KEY_KP2, 'keypad3': uinput.KEY_KP3,
            'keypad4': uinput.KEY_KP4, 'keypad5': uinput.KEY_KP5,
            'keypad6': uinput.KEY_KP6, 'keypad7': uinput.KEY_KP7,
            'keypad8': uinput.KEY_KP8, 'keypad9': uinput.KEY_KP9,
            'keypad0': uinput.KEY_KP0, 'period': uinput.KEY_DOT,
            'capslock': uinput.KEY_CAPSLOCK, 'numlock': uinput.KEY_NUMLOCK,
            'backspace': uinput.KEY_BACKSPACE, 'pause': uinput.KEY_PAUSE,
            'scrolllock': uinput.KEY_SCROLLLOCK, 'backquote': uinput.KEY_GRAVE,
            'comma': uinput.KEY_COMMA, 'minus': uinput.KEY_MINUS,
            'slash': uinput.KEY_SLASH, 'semicolon': uinput.KEY_SEMICOLON,
            'equals': uinput.KEY_EQUAL, 'backslash': uinput.KEY_BACKSLASH,
            'kp_period': uinput.KEY_KPDOT, 'kp_equals': uinput.KEY_KPEQUAL,
            'a': uinput.KEY_A, 'b': uinput.KEY_B, 'c': uinput.KEY_C,
            'd': uinput.KEY_D, 'e': uinput.KEY_E, 'f': uinput.KEY_F,
            'g': uinput.KEY_G, 'h': uinput.KEY_H, 'i': uinput.KEY_I,
            'j': uinput.KEY_J, 'k': uinput.KEY_K, 'l': uinput.KEY_L,
            'm': uinput.KEY_M, 'n': uinput.KEY_N, 'o': uinput.KEY_O,
            'p': uinput.KEY_P, 'q': uinput.KEY_Q, 'r': uinput.KEY_R,
            's': uinput.KEY_S, 't': uinput.KEY_T, 'u': uinput.KEY_U,
            'v': uinput.KEY_V, 'w': uinput.KEY_W, 'x': uinput.KEY_X,
            'y': uinput.KEY_Y, 'z': uinput.KEY_Z
            }


def generate_controller_to_uinput_codes_map():
    """generate a map of keys we actually need
    this will be stored in memory and will comprise of
    a,b,x,y,start,select,l,r,left,right,up,down,l2,r2,l3,r3
    keyboard corresponding values the user has chosen
    in the retroarch.cfg file"""

    c_to_u = {}
    controller_to_keyboard_bindings = get_key_bindings(
        '/opt/retropie/configs/all/retroarch.cfg')
    keyboard_to_uinput_mappings = get_keyboard_to_uinput_map()
    errors = []

    for controller_key in controller_to_keyboard_bindings:
        keyboard_key = controller_to_keyboard_bindings[controller_key]
        try:
            c_to_u[controller_key] = keyboard_to_uinput_mappings[keyboard_key]
        except KeyError as e:
            errors.append(e)

    if (len(errors) > 0):
        print 'The %s keys in your retroarch.cfg are unsupported\
                by this script\n' % ', '.join(map(str, errors))
        print 'Supported keys are:\n'
        print keyboard_to_uinput_mappings.keys()
        sys.exit()

    return c_to_u


def get_key_bindings(ra_cfg):
    """read key mappings from retroarch.cfg file.
    returns the corresponding keys the user mapped
    in the retroarch.cfg file"""

    keys = {}
    with open(ra_cfg, 'r') as fp:
        for line in fp:
<<<<<<< 9ea7e255376d2db0c22efcedfa097b5a640977fd
            if 'input_player1_' in line and '#' not in line and\
                    '_analog_dpad_mode' not in line:
                keys.append(line.split('=')[1][2:-2])
=======
            if 'input_player1_' in line and '#' not in line:
                splitted = line.split('=')
                controller_key = splitted[0].split('_')[-1].strip()
                keyboard_key = splitted[1][2:-2]
                keys[controller_key] = keyboard_key

    # KEYS :{'a': (1, 45), 'b': (1, 44), 'l': (1, 16), 'up': (1, 103),
    # 'down': (1, 108), 'start': (1, 28), 'r': (1, 17), 'right': (1, 106),
    # 'y': (1, 30), 'x': (1, 31), 'select': (1, 54), 'left': (1, 105)}
>>>>>>> Several improvements and fixes:
    return keys


def get_remote_to_controller_bindings(es_cec_cfg):
    """read cec to controller mappings from es-cec file.
    returns the corresponding keys the user mapped in the es-cec.cfg file"""

    # Don't get confused by select key. Remote's select key should trigger
    # 'A' button on game controller(Think it as an enter/ok/double click key).
    # The select button on game controller is used for other stuff in es
    cec_to_controller = {
                         'rewind': 'select', 'yellow': 'select',
                         'fast forward': 'start', 'blue': 'start', 'up': 'up',
                         'left': 'left', 'right': 'right', 'down': 'down',
                         'select': 'a', 'red': 'a', 'exit': 'b', 'green': 'b'}

    if os.path.isfile(es_cec_cfg):
        with open(es_cec_cfg, 'r') as fp:
            for line in fp:
                if '=' in line and '#' not in line:
                    splitted = line.split('=')
                    cec_code = splitted[0].strip()
                    controller_key = splitted[1].strip()
                    print "Overriding "+cec_code+" with "+controller_key
                    cec_to_controller[cec_code] = controller_key
    elif "es-cec.cfg" != es_cec_cfg:
        print '[WARNING] %s does not exist, using defaults...' % es_cec_cfg

    return cec_to_controller


def get_cec_to_uinput_mapping(es_cec_cfg):
    # TODO should we check $HOME/.emulationstation/es_input.cfg?
    esmapping = get_remote_to_controller_bindings(es_cec_cfg)
    keymapping = generate_controller_to_uinput_codes_map()

    es_to_uinput = {}
    errors = {}
    for cec_key in esmapping:
        try:
            es_to_uinput[cec_key] = keymapping[esmapping[cec_key]]
        except KeyError as e:
            errors[cec_key] = esmapping[cec_key]

    # {'blue': (1, 28), 'fast forward': (1, 28), 'right': (1, 106),
    # 'up': (1, 103), 'yellow': (1, 54), 'down': (1, 108), 'exit': (1, 44),
    # 'red': (1, 45), 'rewind': (1, 54), 'green': (1, 44), 'select': (1, 45),
    # 'left': (1, 105)}

    if errors:
        print '[WARNING] The %s controller values in your %s are unsupported \
                by this script. %s in your remote will not work\n' \
              % (', '.join(map(str, errors.values())), es_cec_cfg,
                 ', '.join(map(str, errors.keys())))

    return es_to_uinput


def register_device(uinput_codes):
    return uinput.Device(uinput_codes)


def press_key(line, device, cec_to_uinput):
    """Emulate keyboard presses when a mapped button on the remote control
    has been pressed.

    To navigate ES, only a,b,start,select,up,down,left,and right are required
    x,y,l and r are optional
    """

    # check for key released as pressed was displaying duplicate
    # presses on the remote control used for development

    for cec_key in cec_to_uinput:
        # Maybe we can use a Trie (overkill?)
        if cec_key in line:
            device.emit_click(cec_to_uinput[cec_key])
            break

    # Uncomment the print statement below to display remote output
    # print line


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        if "pressed" in line and "current" in line:
            queue.put(line.lower())
    out.close()


def main():
    ON_POSIX = 'posix' in sys.builtin_module_names

    if len(sys.argv) > 1:
        cfg_file = sys.argv[1]
    else:
        cfg_file = 'es-cec.cfg'

    cecuinputmapping = get_cec_to_uinput_mapping(cfg_file)
    device = register_device(cecuinputmapping.values())

    q = Queue()
    idle = True
    no_cec_on = ['kodi_v7.bin', 'retroarch', 'reicast', 'drastic']
    no_cec_on_cmd = ['-C'+cmd for cmd in no_cec_on]

    while True:
        # only apply key presses when emulation station is running,
        # not in emulators or kodi
        # kodi has its own built in support already
        try:
            _ = subprocess.check_output(['ps']+no_cec_on_cmd)
        except subprocess.CalledProcessError:
            # no 'conflicting' process is present
            if idle:

                # start cec-client to track pressed buttons on remote
                # -d 16 process only debug messages (only lines we care about)
                # https://github.com/Pulse-Eight/libcec/blob/ab6c13846af6d56f26a1632fcde070e9b9c481b4/include/cectypes.h#L812
                p = subprocess.Popen(
                        ['cec-client', '-d', '16'], stdout=subprocess.PIPE,
                        bufsize=1, close_fds=ON_POSIX)
                # https://stackoverflow.com/a/4896288
                t = threading.Thread(target=enqueue_output, args=(p.stdout, q))
                t.start()
                idle = False

            while not q.empty():
                press_key(q.get(), device, cecuinputmapping)

        else:
            # stop cec-client when not in ES
            if not idle:
                p.kill()
                p.wait()  # avoid zombies
                t.join()

                idle = True

            time.sleep(1)


if __name__ == "__main__":
    main()
