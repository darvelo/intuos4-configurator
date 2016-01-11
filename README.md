# intuos4-configurator

Configures the OLEDs and button actions for the Wacom Intuos4 drawing tablet for use in Linux.

This is a quick and dirty implementation, built upon the work of Christoph Karg and Przemo Firszt. I did the bare minimum modifications to Christoph's work to make this run. Thanks, you guys!

# Instructions

1. Clone this repository with `git clone --recursive`
2. Install the dependencies for `i4oled` as mentioned in the README of that directory, then while inside that directory, compile it (you don't need to install it) with:
    * `./autogen.sh`
    * `./configure`
    * `make`
3. Run `./intuos4-configurator -h` for instructions on command-line use.

**Note:**

When running the program, you can manually pass it the path to the `wacom_led` directory within the sysfs `/sys` directory if it can't find it automatically. Setting data on files in this directory for the OLEDs requires sudo privileges.

All Intuos4 button/OLED user configuration should be done within the `settings.xml` file or another XML config file with the same structure, which you can pass to the program as an argument. You can figure out which device to configure with `xsetwacom list`.

# Scripts folder

In here are various useful scripts for the Intuos.

## switch-ring-config.py

Make the wheel button on the Intuos4 switch between four keymap profiles for scrolling the wheel clockwise and counterclockwise, just as it would work with the Wacom software for Windows. You can change the keymap profiles in the code at the top of the script.

Use the intuos4-configurator to set the wheel button to a key combination that invokes this script with sudo.

This script requires sudo privileges to set the wheel LEDs, and should be whitelisted in /etc/sudoers or /etc/sudoers.d/.

## set-pen.sh

This script provides an example of setting a button with `xsetwacom`. Sets the button closest to the pen nib to keypress "alt".

# Resources

Sites and threads with Wacom Intuos4 on Linux information. I read these when putting this project together.

* http://ubuntuforums.org/showthread.php?t=1400425
* http://ubuntuforums.org/showthread.php?t=1380744&page=32
* http://sourceforge.net/p/linuxwacom/bugs/245/
* https://github.com/PrzemoF/i4oled
* http://forums.linuxmint.com/viewtopic.php?f=213&t=127358&sid=2e5dbe482266e14270f318375142d363&start=20
* https://braindump.kargulus.de/?p=432
