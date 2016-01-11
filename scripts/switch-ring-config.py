#!/usr/bin/env python3

'''
Make the wheel button on the Intuos4 switch between four keymap profiles
for scrolling the wheel clockwise and counterclockwise, just as it would
work with the Wacom software for Windows.

Use the intuos4-configurator to set the wheel button to a key combination
that invokes this script with sudo.

This script requires sudo privileges to set the wheel LEDs,
and should be whitelisted in /etc/sudoers or /etc/sudoers.d/.

License: GPLv3

Requirements: xsetwacom

(c) David Arvelo   (david@davidarvelo.com)
'''

import os
import sys
import argparse
import subprocess

# intuos4 wheel scroll functions
# (counterclockwise scroll, clockwise scroll)
PROFILES = (
    ('key [', 'key ]'),
    ('key shift [', 'key shift ]'),
    ('button +4', 'button +5'),
    ('key ctrl minus', 'key ctrl plus'),
)

class WheelProfile:
    def __init__(self, ccw, cw):
        self.cw = cw
        self.ccw = ccw

class Switcher:
    def __init__(self, sysfs_path, device, profiles, verbose=False):
        self.sysfs_path = sysfs_path
        self.profiles = profiles
        self.device = device
        self.verbose = verbose

    def print_verbose(self, command):
        if self.verbose:
            print(*command)

    def switch(self):
        ledIndex = self.getRingState()
        nextIndex = ledIndex+1 if ledIndex < 3 else 0

        self.switchRingLED(nextIndex)
        profile = self.profiles[nextIndex]
        self.setWheelKeys(profile.cw, profile.ccw)

    def getRingState(self):
        with open(os.path.join(self.sysfs_path, 'status_led0_select')) as f:
            return int(f.read().rstrip())

    def switchRingLED(self, which):
        '''
        set which ring led is selected
        0 is first LED, 3 is 4th
        in bash:
            echo 0 | sudo tee /sys/bus/usb/drivers/usbhid/3-2:1.0/XXXX:XXXX:XXXX.XXXX/wacom_led/status_led0_select
        '''
        sysfsfile = os.path.join(self.sysfs_path, 'status_led0_select')
        command = [
            'sudo', 'bash', '-c',
            'echo {} > {}'.format(which, sysfsfile),
        ]

        self.print_verbose(command)
        subprocess.call(command)

    def setWheelKeys(self, cw_key, ccw_key):
        # Wheel clockwise rotation
        command = [
            'xsetwacom',
            '--set', '{}'.format(self.device),
            'AbsWheelDown', cw_key,
        ]

        self.print_verbose(command)
        subprocess.call(command)

        # Wheel counter clockwise rotation
        command = [
            'xsetwacom',
            '--set', '{}'.format(self.device),
            'AbsWheelUp', ccw_key,
        ]

        self.print_verbose(command)
        subprocess.Popen(command)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sysfs-path', action='store', dest='sysfs_path',
                        help='Path to the wacom_led dir in /sys. Example: /sys/bus/hid/drivers/wacom/XXXX:XXXX:XXXX.XXXX/wacom_led')
    parser.add_argument('-d', '--device', action='store', dest='device', default='Wacom Intuos4 6x9 Pad pad',
                        help='Device to configure (string from xsetwacom).')
    parser.add_argument('-l', '--list', action='store_true', dest='listprofiles', default=False,
                        help='List the keys of the available profiles')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                        help='Verbose output')
    return parser.parse_args()

def find_sysfs_path():
    base_dir = '/sys/bus/hid/devices'
    wacom_hid_id = '056A:00B9'
    dirs = os.listdir(base_dir)

    for folder in dirs:
        if folder.find(wacom_hid_id) != -1:
            return os.path.join(base_dir, folder, 'wacom_led')
    else:
        raise Exception('Could not find wacom hid path in {}'.format(base_dir))

def main(args):
    if args.listprofiles:
        print('profiles (counterclockwise scroll, clockwise scroll):')
        print(*PROFILES, sep='\n')
        sys.exit(0)

    sysfs_path = args.sysfs_path or find_sysfs_path()

    if sysfs_path.find('/sys') != 0 or os.path.basename(sysfs_path) != 'wacom_led':
        raise Exception('sysfs path for wacom_led was invalid: {}'.format(sysfs_path))
    if not os.path.isdir(sysfs_path):
        raise Exception('sysfs path for wacom_led was not a directory: {}'.format(sysfs_path))

    profiles = tuple(WheelProfile(*p) for p in PROFILES)
    switcher = Switcher(sysfs_path, args.device, profiles, args.verbose)
    switcher.switch()

if __name__ == '__main__':
    args = parse_args()
    main(args)
