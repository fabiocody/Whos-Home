# Who's Home
[![Build Status](https://travis-ci.org/fabiocody/Whos-Home.svg?branch=master)](https://travis-ci.org/fabiocody/Whos-Home)

This tool analyze the arp table (using arp-scan) to determine who is at home (i.e.: connected to the local network).


### Before using
Make sure you have `arp-scan` installed.
On Debian-like systems:
```
sudo apt-get update && sudo apt-get install arp-scan
```

On macOS (Homebrew):
```
brew install arp-scan
```

### How does it work?
*Who's Home* send an ARP-request to every possible address of your local network; the resulting ARP Table is then parsed, looking for MAC addresses (of which only the last three bytes are taken into account, to ensure compatibility with some network devices that may change the vendor part of the address, e.g.: Wi-Fi repeaters). This is done every 30 seconds.
A person is considered at home if the associated MAC address is found in the ARP table, or if it has been less than 15 minutes since the last time it was found. The reason for this is that *Who's Home* requires that the devices being monitored are connected to the local network. iPhones (and probably others) deliberately disconnect from the network once the screen is turned off to save power, meaning just because the device isn't connected, it doesn't mean that the devices owner isn't at home. Fortunately, iPhones (and probably others) periodically reconnect to the network to check for updates, emails, etc. This program works by keeping track of the last time a device was seen, and comparing that to a threshold value. I've found that a threshold of 15 minutes seems to work well for iPhone, but for different phones this may or may not work.

### .people.json
To make *Who's Home* work, you have to provide a JSON file (located in the same directory as whoshome.py or in your home directory and named `.people.json`) containing the target addresses (only the last 3 bytes) and the corresponding names. Here's an example of how it should look.
```json
[
    { "name": "Bob", "target": "00:00:00" },
    { "name": "John", "target": "aa:bb:cc" }
]
```
Make sure you use colons as separators and lowercase letters in MAC addresses.

### Change threshold
The time threshold is implemented with the integer variable `max_cycles`, whose value is double the value of the threshold in minutes.
The default value is 30 (15 minutes), but you can pass your desired value along with the other arguments.
Please type `whoshome.py -h` for more information.

### Invocation
Please type `whoshome.py -h | --help` for more information.
