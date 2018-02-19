#!/usr/bin/env python3
# whoshome.py

import argparse
import json
from time import sleep
from collections import namedtuple
import socket
import ipaddress
import netifaces
from scapy.all import ARP
from scapy.layers.l2 import arping


__version__ = '2.0.0a'


Person = namedtuple('Person', ['name', 'mac', 'hostname', 'counter'])


class Whoshome:

	def __init__(self, conf_file, output_file=None):
		conf = json.load(conf_file)
		self.__iface = netifaces.ifaddresses(conf['interface'])[netifaces.AF_INET][0]
		self.__iface_addr = ipaddress.ip_interface(self.__iface['addr'] + '/' + self.__iface['netmask'])
		self.__net = ipaddress.ip_network(self.__iface['addr'] + '/' + self.__iface['netmask'], False)
		self.__max_cycles = conf['interface'] if 'interface' in conf.keys() else 30
		self.__output_file = output_file
		self.__people = [
			Person(name=p['name'], mac=p['mac'] if 'mac' in p.keys() else None, hostname=p['hostname'] if 'hostname' in p.keys() else None, counter=self.__max_cycles)
			for p in conf['people']
		]


	def mac_discovery(self):
		for r in arping(self.__iface_addr.compressed, verbose=False)[0]:
			mac = r[1][ARP].hwsrc[9:]
			for p in self.__people:
				if mac == p.mac:
					p.counter = -1

	def mdns_discovery(self):
		for h in self.__net.hosts():
			try:
				hostname = socket.gethostbyaddr(h.exploded)[0]
			except:
				pass
			for p in self.__people:
				if hostname == p.hostname:
					p.counter = -1

	def main(self):
		try:
			while True:
				self.mac_discovery()
				self.mdns_discovery()
				for p in self.__people:
					if p.counter < self.__max_cycles:
						p.counter += 1
				if self.__output_file:
					json.dump(self.__people, self.__output_file)
				sleep(30)
		except KeyboardInterrupt:
			print('\nQuit')
			exit()




if __name__ == '__main__':
	parser = argparse.ArgumentParser('Whoshome')
	parser.add_argument('conf', type=argparse.FileType('r'), help='Path to configuration file')
	parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=None, help='Output file (JSON)')
	args = parser.parse_args()
	Whoshome(args.conf, args.output).main()
