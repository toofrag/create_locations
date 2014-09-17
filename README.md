Create Locations script
=======================

This script is designed to configure network locations on OS X Mavericks. The locations to be created or removed are described in a plist file. 
The script reads the file creates those that do not exist, removes those that should not exist, and ignores those that already exist.

If a location already exists it will make sure the settings match the plist

Careful: Running this script will disrupt the network connection of the client and possibly change its location. 


Locations Plist file
====================

This file contains the descriptions of the locations. It must be called locations.plist and be in the same directory as the script.

keys
----

* *active_locations*: An array of dictionaries. Each dict contains the description of one location.
* *obsolete_locations*: An array of strings. Each string contains the name of a location to delete.
* *default_location*: A string containing the name of the location to switch to after the script has run. (optional)

If the default_location key is not set the script will try to switch to the location that was active before the script was run. If this no longer exists then it will just stay on the last location created.

active_locations dict
---------------------

* *auto_proxy_discovery* : Boolean to enable or disable auto proxy discovery.
* *interface*: String containing the name of the network interface to be used. If "Ethernet" is given the script will search for all ports with ethernet in the name. e.g. USB Ethernet, Thunderbolt Ethernet. 
* *ipv6*: Boolean to enable or disable IPv6. (optional)
* *name*: String containing the name of the network location.
* *http_proxy*: String containing the HTTP proxy URL. (optional)
* *http_proxy_port*:String containg the HTTP proxy port. (optional)
* *https_proxy*: String containing the HTTPS proxy URL. (optional)
* *https_proxy_port*: String containing the HTTPS proxy port. (optional)
* *proxy_exceptions*: String containing the full list of proxy exceptions.

Logging
=======

Each action is logged into /Library/Logs/create_locations.log

Future ideas
============

* Stop using subprocess and start using PyObjC