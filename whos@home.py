#!/usr/bin/env python3

print('Loading...')

import subprocess, sys, json, time, os

# Color class used to print colors
class colors:
	PURPLE = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'

# Analyze argv to extract interface
if len(sys.argv) < 2:
	print(colors.RED + 'ERROR: wrong arguments' + colors.END)
	print(colors.YELLOW + 'Usage:    ' + sys.argv[0] + ' interface' + colors.END)
	exit()
interface = sys.argv[1]

script_path = os.path.dirname(os.path.abspath(__file__)) + '/'

# Open JSON
try:
	people_file = open(script_path + 'people.json', 'r')
	people_json = json.load(people_file)
except:
	print(colors.RED + 'ERROR opening people.json' + colors.END)
	exit()

# Make people list
max_cycles = 30
people = []
allowed = '1234567890abcdef:'
for person_dict in people_json['people']:
	person_dict['target'] = person_dict['target'].lower()
	for c in person_dict['target']:
		if c not in allowed:
			print(colors.RED + 'ERROR: invalid character found in one or more MAC addresses' + colors.END)
			exit()
	if len(person_dict['target']) == 17:
		person_dict['target'] = person_dict['target'][9:]
	people.append(person_dict)
for person_dict in people:
	person_dict['lastSeen'] = max_cycles

def execute_process(bash_command):
    return subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

# Main cycle,
arp_command = 'sudo arp-scan --interface ' + interface + ' --localnet'
while True:
	print()
	output = execute_process(arp_command)
	file = open(script_path + 'people.txt', 'w')  # Write output to a txt file to make presence data available to other programs
	for line in output.stdout.readlines():
		line = line.decode('utf8')
		for split in line.split():
			if len(split) == 17:    # A MAC address is 17 characters long
				mac =  split[9:]    # Only the last 3 bytes of the MAC address are taken into account, to ensure compatibility with some network devices which may change the vendor part of MAC addresses
				for person in people:
					if mac == person['target']:
						person['lastSeen'] = -1    # The counter is set to -1 because every counter will be incremented in the next for cycle
	for person in people:
		if person['lastSeen'] < max_cycles:
			person['lastSeen'] += 1
			print(colors.GREEN + person['name'] + ' is @ home ' + colors.END)
			file.write(person['name'] + ' is @ home \n')
		else:
			print(colors.PURPLE + person['name'] + ' is away ' + colors.END)
			file.write(person['name'] + ' is away \n')
	file.close()
	time.sleep(30)
