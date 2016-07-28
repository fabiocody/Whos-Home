# Whos@Home

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
Whos@home send an ARP-request to every possible address of your local network; the resulting ARP Table is then parsed, looking for MAC addresses (of which only the last three bytes are taken into account, to ensure compatibility with some network devices that may change the vendor part of the address, e.g.: Wi-Fi repeaters). This is done every 30 seconds.
A person is considered at home if the associated MAC address is found in the ARP table, or if it has been less than 15 minutes since the last time it was found. The reason for this is that Whos@Home requires that the devices being monitored are connected to the local network. iPhones (and probably others) deliberately disconnect from the network once the screen is turned off to save power, meaning just because the device isn't connected, it doesn't mean that the devices owner isn't at home. Fortunately, iPhones (and probably others) periodically reconnect to the network to check for updates, emails, etc. This program works by keeping track of the last time a device was seen, and comparing that to a threshold value. I've found that a threshold of 15 minutes seems to work well for iPhone, but for different phones this may or may not work. You can change threshold by changing the `max_cycles` variable at line 34 of whos<i></i>@home.py, remembering that it has to be double the value of the desired threshold in minutes.

### people.json
To make Whos@Home work, you have to provide a JSON file (located in the same directory as whos<i></i>@home.py) containing the target addresses and the corresponding names. Here's an example of how it should look.
```json
{
  "people": [
    { "name": "Bob", "target": "00:00:00" },
    { "name": "John", "target": "aa:bb:cc" }
  ]
}
```
Make sure you use colons as separators and lowercase letters.
