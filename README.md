# Who's Home
[![Build Status](https://travis-ci.org/fabiocody/Whos-Home.svg?branch=master)](https://travis-ci.org/fabiocody/Whos-Home)

This tool uses ARPing to determine who is at home (i.e.: connected to the local network).

**IMPORTANT**  
*Who's Home* works only in Python3.


## How to install
```
pip3 install whoshome
```


## How does it work?
*Who's Home* send an ARP-Request to every possible address of your local network; the answers are then parsed, looking for target's MAC addresses (of which only the last three bytes are taken into account, to ensure compatibility with some network devices that may change the vendor part of the address, e.g.: Wi-Fi repeaters). This is done every 30 seconds.
A person is considered at home if the associated MAC address is found in one of the ARP-Replies, or if it has been less than 15 minutes since the last time it was found. The reason for this is that *Who's Home* requires that the devices being monitored are connected to the local network. iPhones (and probably others) deliberately disconnect from the network once the screen is turned off to save power, but just because the device isn't connected, it doesn't mean that the device's owner isn't at home. Fortunately, iPhones (and probably others) periodically reconnect to the network to check for updates, emails, etc. This tool works by keeping track of the last time a device was seen, and comparing that to a threshold value. I've found that a threshold of 15 minutes seems to work well for iPhone, but for different phones this may or may not work.


## .people.json
To make *Who's Home* work, you have to provide a JSON file (located in your home directory and named `.people.json`) containing the target addresses (only the last 3 bytes) and the corresponding names. Here's an example of how it should look.
```json
[
    { "name": "Bob", "target": "00:00:00" },
    { "name": "John", "target": "aa:bb:cc" }
]
```
Make sure you use colons as separators.


## Change threshold
The time threshold is implemented with the integer variable `max_cycles`, whose value is double the value of the threshold in minutes.
The default value is 30 (15 minutes), but you can pass your desired value along with the other arguments.
Please type `whoshome -h` for more information.


## Invocation
Please type `whoshome -h | --help` for more information.
