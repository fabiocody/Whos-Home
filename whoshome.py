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


def print_help():
	print(Colors.YELLOW + 'Usage:    ' + argv[0] + ' interface [option | filename] [max_cycles]')
	print('Options:')
	print('    -t | txt file output')
	print('    -j | json file output')
	print('    -o | txt and json file output (don\'t write file extension in filename)')
	print('The developer declines every responsibility in case of malfunction due to non observance of this tiny guide' + Colors.END)


def create_json(file):
	json_obj = list()
	for person in people:
		temp_dict = dict()
		temp_dict['name'] = person['name']
		temp_dict['target'] = person['target']
		temp_dict['home'] = bool(person['lastSeen'] < max_cycles)
		json_obj.append(temp_dict)
	json.dump(json_obj, file)


# Check if arp-scan is installed
if os.system('type arp-scan 1>/dev/null 2>/dev/null'):
	print(Colors.RED + 'ERROR: arp-scan not installed' + Colors.END)
	exit()


# Analyze argv to extract interface and file output mode
interface = str()
output_file_mode = 'no'
output_filename = str()
argc = len(argv)
max_cycles = 30
if argc < 2 or argc > 5:
	print(Colors.RED + 'ERROR: wrong arguments' + Colors.END)
	print_help()
	exit()
else:
	if argv[1] == '-h' or argv[1] == '--help':
		print_help()
		exit()
	interface = argv[1]
	if argc % 2:
		max_cycles = int(argv[argc - 1])
	if argc >= 4:
		if argv[2] == '-j':
			output_file_mode = 'json'
			output_filename = argv[3]
			if output_filename[-4:] != output_file_mode:
				print(Colors.RED + 'ERROR: file extension' + Colors.END)
				exit()
		elif argv[2] == '-t':
			output_file_mode = 'txt'
			output_filename = argv[3]
			if output_filename[-3:] != output_file_mode:
				print(Colors.RED + 'ERROR: file extension' + Colors.END)
				exit()
		elif argv[2] == '-o':
			output_file_mode = 'both'
			output_filename = argv[3]
			if output_filename == "people":		# Refuse 'people' as filename to avoid conflicts with people.json (config file)
				print(Colors.RED + 'ERROR: invalid name' + Colors.END)
				exit()
		else:
			print(Colors.RED + 'ERROR: wrong arguments' + Colors.END)
			print_help()
			exit()


script_path = os.path.dirname(os.path.abspath(__file__)) + '/'


# Open people.json
try:
	people_file = open(script_path + 'people.json', 'r')
	people_json = json.load(people_file)
except:
	print(Colors.RED + 'ERROR opening people.json' + Colors.END)
	exit()


# Make people list
people = list()
allowed = '1234567890abcdef:'
for person_dict in people_json:
	person_dict['target'] = person_dict['target'].lower()
	for c in person_dict['target']:
		if c not in allowed:
			print(Colors.RED + 'ERROR: invalid character found in one or more MAC addresses' + Colors.END)
			exit()
	if len(person_dict['target']) == 17:
		person_dict['target'] = person_dict['target'][9:]
	people.append(person_dict)
for person_dict in people:
	person_dict['lastSeen'] = max_cycles


# Main cycle
arp_command = 'sudo arp-scan --interface ' + interface + ' --localnet'
while True:
	output = getstatusoutput(arp_command)[1]
	if output_file_mode != 'no':
		if output_file_mode != 'both':
			file = open(output_filename, 'w')
		else:
			file_txt = open(output_filename + '.txt', 'w')
			file_json = open(output_filename + '.json', 'w')
	for line in output.split('\n'):
		for split in line.split():
			if len(split) == 17:    # A MAC address is 17 characters long
				mac = split[9:]    # Only the last 3 bytes of the MAC address are taken into account, to ensure compatibility with some network devices which may change the vendor part of MAC addresses
				for person in people:
					if mac == person['target']:
						person['lastSeen'] = -1    # The counter is set to -1 because every counter will be incremented in the next 'for' cycle
	for person in people:
		if person['lastSeen'] < max_cycles:
			person['lastSeen'] += 1
			print(Colors.GREEN + person['name'] + ' is home  🏡' + Colors.END)
			if output_file_mode == 'txt':
				file.write(person['name'] + ' is home  🏡\n')
			elif output_file_mode == 'both':
				file_txt.write(person['name'] + ' is home  🏡\n')
		else:
			print(Colors.PURPLE + person['name'] + ' is away  🌍' + Colors.END)
			if output_file_mode == 'txt':
				file.write(person['name'] + ' is away  🌍\n')
			elif output_file_mode == 'both':
				file_txt.write(person['name'] + ' is away  🌍\n')
	print()

	if output_file_mode != 'no':
		if output_file_mode == 'json':
			create_json(file)
		elif output_file_mode == 'both':
			create_json(file_json)
		try:
			file_txt.close()
			file_json.close()
		except:
			file.close()

	try:
		sleep(30)
	except KeyboardInterrupt:
		print('\nQuit')
		exit()
