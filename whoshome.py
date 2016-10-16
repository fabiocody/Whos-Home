#!/usr/bin/env python3

import os
import json
from sys import argv
from time import sleep
from subprocess import getstatusoutput
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
logger = logging.getLogger('whoshome')
from scapy.all import ARP
from scapy.layers.l2 import arping
from getpass import getuser
import platform
from pwd import getpwall
import argparse


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
        self._logging_level = args[4]
        # Remove logging handlers to reset logging facilities
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(format='[*] %(levelname)s : %(module)s : %(message)s',
                            level=self._logging_level)
        self._people = self._make_people_list(self._open_people_file())

    def _open_people_file(self):
        # Try to open .people.json in every user's home directory. This should
        # work since there should be just one config file system-wide.
        logger.info('opening .people.json')
        for p in getpwall():
            home_path = os.path.expanduser('~' + p[0]) + '/'
            try:
                people_json = None
                people_file = open(home_path + '.people.json', 'r')
                logger.debug('.people. opened')

                people_json = json.load(people_file)
                people_file.close()
                logger.debug('.people.json closed')
                break
            except:
                pass
        if people_json == None:
            logger.error('cannot open .people.json')
            exit(1)
        else:
            return people_json

    def _make_people_list(self, people_json):
        logger.info('making people list')
        people = list()
        allowed = '1234567890abcdef:'
        for person_dict in people_json:
            person_dict['target'] = person_dict['target'].lower()
            logger.debug('checking MAC address ' + person_dict['target'])
            for c in person_dict['target']:
                if c not in allowed:
                    logger.error('invalid character found in ' +
                                  person_dict['name'] + '\'s MAC address ' + person_dict['target'])
                    exit(1)
            # A MAC address is 17 characters long. Only the last 3 bytes of the MAC
            # address are taken into account, to ensure compatibility with some
            # network devices which may change the vendor part of MAC addresses
            if len(person_dict['target']) == 17:
                person_dict['target'] = person_dict['target'][9:]
            elif len(person_dict['target']) != 8:
                logger.error('invalid MAC address length ' + person_dict['target'])
                exit(1)
            people.append(person_dict)
        for person in people:
            logger.debug('initializing counter for {mac}'.format(mac=person['target']))
            person['last_seen'] = self._max_cycles
        return people

    def _create_json(self, file):
        logger.info('creating output JSON')
        json_obj = list()
        for person in self._people:
            temp_dict = dict()
            temp_dict['name'] = person['name']
            temp_dict['target'] = person['target']
            temp_dict['home'] = bool(person['last_seen'] < self._max_cycles)
            json_obj.append(temp_dict)
        json.dump(json_obj, file, indent=4)

    def _get_ip_from_interface(self):
        logger.info('getting IP address from interface name')
        output = getstatusoutput('ip a | grep ' + self._interface + ' | grep inet')
        if output[0] == 0:
            return output[1][output[1].find('inet') + 5: output[1].find('brd') - 1]
        else:
            logger.error('invalid interface')
            exit(1)

    def cycle(self):
        logger.info('starting cycle')
        while True:
            logger.debug('cycling')
            try:
                logger.debug('ARPINGing')
                results, unanswered = arping(self._get_ip_from_interface(), verbose=False)
                if self._output_file_mode != 'no':
                    if self._output_file_mode != 'both':
                        file = open(self._output_filename, 'w')
                    else:
                        file_txt = open(self._output_filename + '.txt', 'w')
                        file_json = open(self._output_filename + '.json', 'w')
                logger.debug('parsing results')
                for result in results:
                    # A MAC address is 17 characters long. Only the last 3 bytes of the MAC
                    # address are taken into account, to ensure compatibility with some
                    # network devices which may change the vendor part of MAC addresses
                    mac = result[1][ARP].hwsrc[9:]
                    for person in self._people:
                        if mac == person['target']:
                            # The counter is set to -1 because every counter will be incremented in
                            # the next 'for' cycle
                            person['last_seen'] = -1
                for person in self._people:
                    if person['last_seen'] < self._max_cycles:
                        person['last_seen'] += 1
                        print(Colors.GREEN + '🏡  ' + person['name'] + ' is home' + Colors.END)
                        if self._output_file_mode == 'txt':
                            file.write('🏡 ' + person['name'] + ' is home\n')
                        elif self._output_file_mode == 'both':
                            file_txt.write('🏡 ' + person['name'] + ' is home\n')
                    else:
                        print(Colors.YELLOW + '🌍  ' + person['name'] + ' is away' + Colors.END)
                        if self._output_file_mode == 'txt':
                            file.write('🌍 ' + person['name'] + ' is away\n')
                        elif self._output_file_mode == 'both':
                            file_txt.write('🌍 ' + person['name'] + ' is away\n')
                logger.debug('handling file output')
                print()
                if self._output_file_mode != 'no':
                    if self._output_file_mode == 'json':
                        self._create_json(file)
                    elif self._output_file_mode == 'both':
                        self._create_json(file_json)
                    try:
                        file_txt.close()
                        file_json.close()
                    except:
                        file.close()
                sleep(30)
            except KeyboardInterrupt:
                print('\nQuit')
                exit(0)


def print_help():
    print(Colors.YELLOW + 'Usage:    ' + argv[0] + ' interface [option | filename] [max_cycles]')
    print('Options:')
    print('    -t | txt file output')
    print('    -j | json file output')
    print('    -o | txt and json file output (don\'t write file extension in filename)')
    print('The developer declines every responsibility in case of malfunction due to non observance of this tiny guide' + Colors.END)


def check_environment():
    logger.info('checking environment')
    if platform.system() != 'Linux':
        logger.error('system not supported')
        exit(1)
    if getuser() != 'root':
        logger.error('please run as root')
        parse_argv()
        exit(1)


def parse_argv(passed_args=None):
    logger.info('parsing arguments')
    parser = argparse.ArgumentParser(
        description='Who\'s Home  -  Find out who\'s home based on Wi-Fi connection')
    parser.add_argument('interface', type=str, help='Interface used to send ARP-Requests.')
    parser.add_argument('-o', '--output', type=str,
                        help='Send results to a file. Available file extensions are \'.txt\' and \'.json\'. The file format will be inferred from the file extension. If you want to have both file formats, omit the file extension.')
    parser.add_argument('-c', '--max-cycles', type=int, default=30,
                        help='Alter `max_cycles` variable to modify the period of time in which a person is considered at home.')
    parser.add_argument('-l', '--log', type=str, help='Set logging level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING')
    args = parser.parse_args(passed_args)
    interface = args.interface
    if args.output == None:
        output_file_mode = 'no'
        output_filename = str()
    else:
        allowed_extensions = ['txt', 'json']
        file_split = args.output.split('.')
        file_extension = file_split[-1]
        if file_extension in allowed_extensions:
            output_file_mode = file_extension
            output_filename = args.output
        else:
            output_file_mode = 'both'
            output_filename = args.output
    max_cycles = args.max_cycles
    logging_level = getattr(logging, args.log)
    return (interface, output_file_mode, output_filename, max_cycles, logging_level)


def main():
    logging.basicConfig(format='[*] %(levelname)s : %(module)s : %(message)s')
    check_environment()
    wh = Whoshome(parse_argv())
    wh.cycle()


if __name__ == '__main__':
    main()
