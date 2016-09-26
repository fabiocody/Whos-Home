#!/usr/bin/env python3

import os
import json
from sys import argv
from time import sleep
from subprocess import getstatusoutput


# Color class used to print colors
class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Whoshome:

    def __init__(self, args):
        self._interface = args[0]
        self._output_file_mode = args[1]
        self._output_filename = args[2]
        self._max_cycles = args[3]
        self._people = self.make_people_list(self.open_people_file())

    def open_people_file(self):
        try:
            people_file = open(home_path + '.people.json', 'r')
            people_json = json.load(people_file)
            people_file.close()
        except:
            print(Colors.RED + 'ERROR opening .people.json' + Colors.END)
            exit(1)
        return people_json

    def make_people_list(self, people_json):
        people = list()
        allowed = '1234567890abcdef:'
        for person_dict in people_json:
            person_dict['target'] = person_dict['target'].lower()
            for c in person_dict['target']:
                if c not in allowed:
                    print(Colors.RED + 'ERROR: invalid character found in one or more MAC addresses' + Colors.END)
                    exit(1)
            if len(person_dict['target']) == 17:
                person_dict['target'] = person_dict['target'][9:]
            people.append(person_dict)
        for person in people:
            person['last_seen'] = self._max_cycles
        return people

    def cycle(self):
        arp_command = 'sudo arp-scan --interface ' + self._interface + ' --localnet'
        while True:
            output = getstatusoutput(arp_command)[1]
            if self._output_file_mode != 'no':
                if self._output_file_mode != 'both':
                    file = open(self._output_filename, 'w')
                else:
                    file_txt = open(self._output_filename + '.txt', 'w')
                    file_json = open(self._output_filename + '.json', 'w')
            for line in output.split('\n'):
                for split in line.split():
                    if len(split) == 17:    # A MAC address is 17 characters long
                        # Only the last 3 bytes of the MAC address are taken into account, to
                        # ensure compatibility with some network devices which may change the
                        # vendor part of MAC addresses
                        mac = split[9:]
                        for person in self._people:
                            if mac == person['target']:
                                # The counter is set to -1 because every counter will be incremented
                                # in the next 'for' cycle
                                person['last_seen'] = -1
            for person in self._people:
                if person['last_seen'] < self._max_cycles:
                    person['last_seen'] += 1
                    print(Colors.GREEN + '🏡 ' + person['name'] + ' is home' + Colors.END)
                    if self._output_file_mode == 'txt':
                        file.write('🏡 ' + person['name'] + ' is home\n')
                    elif self._output_file_mode == 'both':
                        file_txt.write('🏡 ' + person['name'] + ' is home\n')
                else:
                    print(Colors.PURPLE + '🌍 ' + person['name'] + ' is away' + Colors.END)
                    if self._output_file_mode == 'txt':
                        file.write('🌍 ' + person['name'] + ' is away\n')
                    elif self._output_file_mode == 'both':
                        file_txt.write('🌍 ' + person['name'] + ' is away\n')
            print()
            if self._output_file_mode != 'no':
                if self._output_file_mode == 'json':
                    self.create_json(file)
                elif self._output_file_mode == 'both':
                    self.create_json(file_json)
                try:
                    file_txt.close()
                    file_json.close()
                except:
                    file.close()
            try:
                sleep(30)
            except KeyboardInterrupt:
                print('\nQuit')
                exit(0)

    def create_json(self, file):
        json_obj = list()
        for person in self._people:
            temp_dict = dict()
            temp_dict['name'] = person['name']
            temp_dict['target'] = person['target']
            temp_dict['home'] = bool(person['last_seen'] < self._max_cycles)
            json_obj.append(temp_dict)
        json.dump(json_obj, file)


def print_help():
    print(Colors.YELLOW + 'Usage:    ' + argv[0] + ' interface [option | filename] [max_cycles]')
    print('Options:')
    print('    -t | txt file output')
    print('    -j | json file output')
    print('    -o | txt and json file output (don\'t write file extension in filename)')
    print('The developer declines every responsibility in case of malfunction due to non observance of this tiny guide' + Colors.END)


def check_dependencies():		# Check if arp-scan is installed
    if os.system('type arp-scan 1>/dev/null 2>/dev/null'):
        print(Colors.RED + 'ERROR: arp-scan not installed' + Colors.END)
        exit(1)


def parse_argv():
    argc = len(argv)
    interface = str()
    output_file_mode = 'no'
    output_filename = str()
    max_cycles = 30
    if argc < 2 or argc > 5:
        print(Colors.RED + 'ERROR: wrong arguments' + Colors.END)
        print_help()
        exit(1)
    else:
        if argv[1] == '-h' or argv[1] == '--help':
            print_help()
            exit(1)
        interface = argv[1]
        if argc % 2:
            max_cycles = int(argv[argc - 1])
        if argc >= 4:
            if argv[2] == '-j':
                output_file_mode = 'json'
                output_filename = argv[3]
                if output_filename[-4:] != output_file_mode:
                    print(Colors.RED + 'ERROR: file extension' + Colors.END)
                    exit(1)
            elif argv[2] == '-t':
                output_file_mode = 'txt'
                output_filename = argv[3]
                if output_filename[-3:] != output_file_mode:
                    print(Colors.RED + 'ERROR: file extension' + Colors.END)
                    exit(1)
            elif argv[2] == '-o':
                output_file_mode = 'both'
                output_filename = argv[3]
            else:
                print(Colors.RED + 'ERROR: wrong arguments' + Colors.END)
                print_help()
                exit(1)
    return (interface, output_file_mode, output_filename, max_cycles)


#script_path = os.path.dirname(os.path.abspath(__file__)) + '/'
home_path = os.path.expanduser('~') + '/'


def main():
    check_dependencies()
    wh = Whoshome(parse_argv())
    wh.cycle()


if __name__ == '__main__':
    main()
