#!/usr/bin/env python3

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

max_cycles = 30
people = []
for person_dict in people_json['people']:
	person_dict['target'] = person_dict['target'].lower()
	people.append(person_dict)
for person_dict in people:
	person_dict['lastSeen'] = max_cycles

def execute_process(bash_command):
    return subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

arp_command = 'sudo arp-scan --interface ' + interface + ' --localnet'
while True:
	output = execute_process(arp_command)
	file = open(script_path + 'people.txt', 'w')
	for line in output.stdout.readlines():
		line = line.decode('utf8')
		for split in line.split():
			if len(split) == 17:
				mac =  split[9:]
				#print(mac)
				for person in people:
					#print(person['target'])
					if mac == person['target']:
						person['lastSeen'] = -1
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
	print()
