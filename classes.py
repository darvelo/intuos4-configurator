'''
Data structures for intuos4 profiles

License: GPLv3

(c) Christoph Karg (christoph@kargulus.de)
    David Arvelo   (david@davidarvelo.com)
'''
import os
import subprocess
from xml.etree import ElementTree

class ProfileStorage:
    def __init__(self):
        self.__profiles_dict = {}
        self.__default_profile = None

    def getDefaultProfile(self):
        return self.__default_profile

    def getListOfProfiles(self):
        return self.__profiles_dict.keys()

    def getDevice(self):
        return self.__device

    def addProfile(self, profile):
        self.__profiles_dict[profile.getName()] = profile

    def getProfile(self, name):
        return self.__profiles_dict[name]

    def extractProfile(self, profile):
        profile_name = profile.attrib['name']
        lefthanded = profile.attrib['lefthanded']
        if lefthanded != None and lefthanded.lower() == 'true':
            lefthanded = True
        else:
            lefthanded = False

        if profile_name == None:
            raise Exception('Profile did not have a name.')

        p = Profile()
        p.setName(profile_name)

        if lefthanded:
            p.setOrientation(True)
        else:
            p.setOrientation(False)

        button_list = profile.findall('button')
        for button in button_list:
            b = Button(button)
            p.setButton(b)

        wheel = profile.find('wheel')
        if wheel != None:
            w = Wheel()
            if 'button' in wheel.attrib:
                w.setButtonKey(wheel.attrib['button'])
            if 'clockwise' in wheel.attrib:
                w.setClockwiseKey(wheel.attrib['clockwise'])
            if 'counterclockwise' in wheel.attrib:
                w.setCounterClockwiseKey(wheel.attrib['counterclockwise'])
            p.setWheel(w)
        return p

    def dump(self):
        print(self)

    def __str__(self):
        return ''.join(
            ['\n', 'ProfileStorage(): ', '\n'] +
            [str(p) for p in self.__profiles_dict.values()]
        )

    def readFile(self,filename):

        self.__profiles_dict = {}

        tree = ElementTree.parse(filename)

        root = tree.getroot()

        if 'device' in root.attrib:
            self.__device = root.attrib['device']

        profiles = root.find('profiles')

        self.__default_profile = profiles.attrib['default']

        profile_list = profiles.findall('profile')

        for p in profile_list:
            x = self.extractProfile(p)
            self.addProfile(x)


class Profile:
    __name = ''
    __left_handed = False
    __button_dict = {}


    def __init__(self):
        self.__button_dict = {}
        for i in range(0, 8):
            button = Button()
            button.setNumber(i)
            self.__button_dict[i] = button
        self.__wheel = Wheel()

    def getButton(self, number):
        return self.__button_dict[number]

    def setButton(self, button):
        self.__button_dict[button.getNumber()] = button

    def setName(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def setWheel(self, wheel):
        self.__wheel = wheel

    def getWheel(self):
        return self.__wheel

    def setOrientation(self, left_handed):
        self.__left_handed = left_handed

    def isLeftHanded(self):
        return self.__left_handed

    def dump(self):
        print(self)

    def __str__(self):
        return '\n'.join(
            [
                'Profile(): ',
                'Name......: ' + str(self.__name),
                'Lefthanded: ' + str(self.__left_handed)
            ] +
            [str(self.__button_dict[i]) for i in self.__button_dict.keys()] + [str(self.__wheel)]
        )

''' Button '''
class Button:
    def __init__(self, button_xml_node=None):
        if button_xml_node != None:
            oled = button_xml_node.find('oled')
            type = oled.attrib['type'] or 'image'
            name = oled.attrib['name'] or 'debian.png'
            number = int(button_xml_node.attrib['number'])
            number = 0 if number is None else number
            keystroke = button_xml_node.find('keystroke')
            if keystroke != None:
                keystroke = keystroke.attrib['key']
            else:
                keystroke = 'shift'
        else:
            type = 'image'
            name = 'debian.png'
            number = 0
            keystroke = ''

        self.__number = number
        self.__type = type
        self.__name = name
        self.__keystroke = keystroke

        if self.__type == 'image':
            self.__name = os.path.join(
                os.path.dirname(__file__),
                'icons',
                self.__name,
            )

        self.validate()

    def validate(self):
        '''Check button values are valid'''
        if self.__number < 0 or self.__number > 7:
            raise Exception('Button number out of range.')

        if self.__type == 'image':
            if not os.path.isfile(self.__name):
                raise Exception('OLED image file was not found: {}'.format(self.__name))
        elif self.__type == 'text':
            pass
        else:
            raise Exception('OLED config Type was invalid.')

    def getNumber(self):
        return self.__number

    def setNumber(self, number):
        self.__number = int(number)

    def getType(self):
        return self.__type

    def getName(self):
        return self.__name

    def getKeystroke(self):
        return self.__keystroke

    def dump(self):
        print(self)

    def __str__(self):
        return ''.join([
            'Button(): ',
            'Number =', str(self.__number), ', ',
            'type =', str(self.__type), ', ',
            'name =', str(self.__name), ', ',
            'keystroke =', str(self.__keystroke),
        ])


class Wheel:
    def __init__(self, button_key='', clockwise_key='', counterclockwise_key=''):
        self.setButtonKey(button_key)
        self.setClockwiseKey(clockwise_key)
        self.setCounterClockwiseKey(counterclockwise_key)

    def getButtonKey(self):
        return self.__button_key

    def setButtonKey(self, button_key):
        self.__button_key = button_key

    def getClockwiseKey(self):
        return self.__clockwise_key

    def setClockwiseKey(self, clockwise_key=''):
        self.__clockwise_key = clockwise_key

    def getCounterClockwiseKey(self):
        return self.__counterclockwise_key

    def setCounterClockwiseKey(self, counterclockwise_key=''):
        self.__counterclockwise_key = counterclockwise_key

    def dump(self):
        print(self)

    def __str__(self):
        return ''.join([
            'Wheel(): ',
            'Button Key: ' + str(self.__button_key),
            'Clockwise Key: ' + str(self.__clockwise_key),
            'Counterclockwise Key: ' + str(self.__counterclockwise_key),
        ])


class Tablet:
    '''
    Functions for interaction with the tablet
    '''

    __led_config = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'i4oled/src/i4oled',
    ))

    __xsetwacom = 'xsetwacom'
    __device = 'Wacom Intuos4 6x9 Pad pad'
    __init_ok = False
    __verbose = False

    __wheel_button = 'button 1'
    __wheel_clockwise_button = 'AbsWheelDown'
    __wheel_counter_clockwise_button = 'AbsWheelUp'

    __button_dict = {
        0: 'button 2',
        1: 'button 3',
        2: 'button 8',
        3: 'button 9',
        4: 'button 10',
        5: 'button 11',
        6: 'button 12',
        7: 'button 13',
    }

    def __init__(self, sys_wacom_led_path):
        self.__sysfs_path = sys_wacom_led_path
        searchpath = ['~/bin', '/usr/local/bin', '/usr/bin', '/opt/bin']
        self.__init_ok = False

        # Searching for xsetwacom
        for p in searchpath:
            if os.path.isfile(os.path.expanduser(p + '/' + self.__xsetwacom)):
                self.__xsetwacom = os.path.expanduser(p + '/' + self.__xsetwacom)
                print('Found xsetwacom in ', p)
                break
        else:
            print('xsetwacom not found.')
            return

        # Searching for i4oled
        if os.path.isfile(self.__led_config):
            print('Found i4oled in ', self.__led_config)
        else:
            print('i4oled not found in ', self.__led_config)
            return

        self.__init_ok = True

    def initOk(self):
        return self.__init_ok

    def setProfile(self, profile):
        print('setting profile', profile)
        self.switchRingLED(0)
        self.setRingLEDLuminance(10)
        self.setButtonsLuminance(15)
        self.setTapTime(0)
        for i in range(0, 8):
            self.setButtonImage(i, profile)
            self.setButtonKeys(i, profile)
        self.setWheelKeys(profile)

    def switchRingLED(self, which):
        '''
        set which ring led is selected
        0 is first LED, 3 is 4th
        in bash:
            echo 0 | sudo tee /sys/bus/usb/drivers/usbhid/3-2:1.0/XXXX:XXXX:XXXX.XXXX/wacom_led/status_led0_select
        '''
        sysfsfile = os.path.join(self.__sysfs_path, 'status_led0_select')
        command = [
            'sudo', 'bash', '-c',
            'echo {} > {}'.format(which, sysfsfile),
        ]

        self.printVerbose(command)
        subprocess.call(command)

    def setRingLEDLuminance(self, luminance):
        '''
        set ring led brightness
        3 seems to be minimum, 10 seems to be max
        not sure what the "status1_luminance" file is for
        in bash:
            echo 10 | sudo tee /sys/bus/usb/drivers/usbhid/3-2:1.0/XXXX:XXXX:XXXX.XXXX/wacom_led/status0_luminance
        '''
        sysfsfile = os.path.join(self.__sysfs_path, 'status0_luminance')
        command = [
            'sudo', 'bash', '-c',
            'echo {} > {}'.format(luminance, sysfsfile),
        ]

        self.printVerbose(command)
        subprocess.call(command)

    def setButtonsLuminance(self, luminance):
        '''
        set button led brightness
        0 is darkest (invisible), 15 is brightest for my tablet (intuos4)
        in bash:
            echo 15 | sudo tee /sys/bus/usb/drivers/usbhid/3-2:1.0/XXXX:XXXX:XXXX.XXXX/wacom_led/buttons_luminance
        '''
        sysfsfile = os.path.join(self.__sysfs_path, 'buttons_luminance')
        command = [
            'sudo', 'bash', '-c',
            'echo {} > {}'.format(luminance, sysfsfile),
        ]

        self.printVerbose(command)
        subprocess.call(command)

    def setButtonImage(self, i, profile):
        b = profile.getButton(i)
        if profile.isLeftHanded():
            i = 7-i
        sysbutton = os.path.join(self.__sysfs_path, 'button{}_rawimg'.format(i))

        command = [
            'sudo',
            self.__led_config,
            '--device', sysbutton,
        ]

        if b.getType() == 'text':
            command += ['--text', b.getName()]
        elif b.getType() == 'image':
            command += ['--image', os.path.expanduser(b.getName())]

        self.printVerbose(command)
        subprocess.call(command)

    def setButtonKeys(self, i, profile):
        b = profile.getButton(i)
        command = [
            'xsetwacom',
            '--set', '{}'.format(self.__device),
        ]
        if profile.isLeftHanded():
            command += self.__button_dict[7 - i].split(' ')
        else:
            command += self.__button_dict[i].split(' ')

        command += ['key {}'.format(b.getKeystroke())]

        self.printVerbose(command)
        subprocess.call(command)

    def mapScrollWheelOrKeypress(self, key):
        if key in ['4', '+4', '5', '+5']:
            # map mouse scroll wheel "buttons" manually
            return 'button ' + key
        else:
            # anything else we will assume is a keypress
            return 'key ' + key

    def setWheelKeys(self, profile):
        # Setting wheel keys
        w = profile.getWheel()
        # Button
        command = [
            self.__xsetwacom,
            '--set', '{}'.format(self.__device),
        ]
        command += self.__wheel_button.split(' ')
        command.append('key {}'.format(w.getButtonKey()))

        self.printVerbose(command)
        subprocess.call(command)

        # Wheel clockwise rotation
        command = [
            self.__xsetwacom,
            '--set', '{}'.format(self.__device),
            self.__wheel_clockwise_button,
            self.mapScrollWheelOrKeypress(w.getClockwiseKey())
        ]

        self.printVerbose(command)
        subprocess.call(command)

        # Wheel counter clockwise rotation
        command = [
            self.__xsetwacom,
            '--set', '{}'.format(self.__device),
            self.__wheel_counter_clockwise_button,
            self.mapScrollWheelOrKeypress(w.getCounterClockwiseKey())
        ]

        self.printVerbose(command)
        subprocess.Popen(command)

    def setTapTime(self, tapTime):
        command = [
            'xsetwacom',
            '--set', '{}'.format(self.__device),
            'TapTime', str(tapTime)
        ]

        self.printVerbose(command)
        subprocess.call(command)

    def setDevice(self, device):
        self.__device = device

    def printVerbose(self, msg):
        if self.__verbose == True:
            print(*msg)

    def setVerboseMode(self, mode):
        self.__verbose = mode
