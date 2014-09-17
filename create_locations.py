#!/usr/bin/python

import subprocess
from plistlib import *
import os
import re
import logging
from datetime import datetime


def chomp(chomp_input):
    import re
    chomp_output = re.sub('[\n\r\s]$', '', chomp_input)
    return chomp_output


# Get list of current locations
def get_current_locations():
    # Runs /usr/sbin/networksetup -listlocations    
    # Returns a list with current locations
    return_list = []
    listLocationsCommand = ["/usr/sbin/networksetup", "-listlocations"]
    try:
        raw_locations = subprocess.check_output(listLocationsCommand, shell=False)
    except:
        logging.error("Unable to get locations")
        return return_list
    # Split each line   
    for line in raw_locations.split('\n'):
        # Strip out empty lines
        if len(line) > 0:
            return_list.append(line)
    return return_list


def get_current_selected_location():
    '''Returns the current selected location'''
    selectedLocationCommand = ["/usr/sbin/networksetup", "-getcurrentlocation"]
    try:
        selected_location = subprocess.check_output(selectedLocationCommand, shell=False)
    except:
        logging.error("Unable to get selected locations")
        selected_location = ""
    return selected_location


def remove_location(location_name):
    # Deletes a location.
    # Returns True or False
    # Check location exsts
    if not location_name in get_current_locations():
        log_message = "Location '{}' does not exist".format(location_name)
        logging.info(log_message)
        return False
    delete_location_command = ["/usr/sbin/networksetup", "-deletelocation", location_name]
    try:
        subprocess.call(delete_location_command, shell=False, stderr=None,stdout=None)
    except:
        logging.error("Deleting location failed")
        return False
    return True


def create_location(location_name):
    # Creates a location
    # Returns True or False 
    if location_name in get_current_locations():
        log_message = "Location '{}' already exists".format(location_name)
        logging.info(log_message)
        return False
    create_location_command = ["/usr/sbin/networksetup", "-createlocation", location_name, "populate", "2>&1"]
    try:
        subprocess.call(create_location_command, shell=False)
    except:
        logging.error("Creating location failed")
        return False
    return True


def switch_location(new_location):
    if new_location in get_current_locations():
        switch_location_command = ["/usr/sbin/networksetup", "-switchtolocation", new_location]
        try:
            subprocess.check_output(switch_location_command, shell=False)
        except:
            logging.error("Unable to switch location")


def disable_service(service_name):
    log_message = "Disabling {}".format(service_name)
    logging.info(log_message)
    disable_network_services = ["/usr/sbin/networksetup", "-setnetworkserviceenabled", service_name, "off"]
    try:
        disable_service_command = subprocess.check_output(disable_network_services, shell=False)
    except:
        log_message = "Unable to disable service {}".format(service_name)
        logging.error(log_message)


def enable_service(service_name):
    log_message = "Enabling {}".format(service_name)
    logging.info(log_message)
    enable_network_services = ["/usr/sbin/networksetup", "-setnetworkserviceenabled", service_name, "on"]
    try:
        enable_service_command = subprocess.check_output(enable_network_services, shell=False)
    except:
        log_message = "Unable to enable service {}".format(service_name)
        logging.error(log_message)


def get_actual_ethernet_service(service_name):
    if service_name == "Ethernet":
        for enet_seak in get_network_services():
            if re.search("[e|E]thernet", enet_seak) != None:
                if enet_seak[0] == "*":
                    service_name = enet_seak[1:]
                else:
                    service_name = enet_seak
                log_message = "Actual ethernet port = {}".format(service_name)
                logging.info(log_message)
    return service_name


def disable_unnecessary_net_services(service_to_keep):
    ''' Disables all the network services, except the one specified.'''
    if not service_to_keep in get_network_services():
        log_message = "{} is not available".format(service_to_keep)
        logging.info(log_message)
    for service in get_network_services():
        # Enable the service_to_keep
        if re.search(re.escape(service_to_keep), service) != None:
            enable_service(service_to_keep)
        else:
            # Disable not the service_to_keep
            if service[0] == "*":
                log_message = "{} already disabled".format(service)
                logging.info(log_message)
            else:
                disable_service(service)


def get_network_services():
    ''' Gets the available network services in the current locations
    Returns a list of all items
    networksetup -listallnetworkservices '''
    return_list = []
    list_network_services = ["/usr/sbin/networksetup", "-listallnetworkservices"]
    try:
        raw_services = subprocess.check_output(list_network_services, shell=False)
    except:
        logging.error("Unable to get network services")
        return return_list
    # Split each line   
    for line in raw_services.split('\n'):
        # Strip out empty lines
        if len(line) > 0:
            if not line == "An asterisk (*) denotes that a network service is disabled.":
                return_list.append(line)
    return return_list


def set_proxy(proxy, proxy_port, protocol, service, exceptions):
    proxy_state = "off"
    if protocol == "http":
        netsetup_protocol = "web"
    elif protocol == "https":
        netsetup_protocol = "secureweb"
    else:
        return False

    if proxy != "":
        proxy_state = "on"
        log_message = "Setting {0} proxy to {1}:{2} on {3}".format(protocol, proxy, proxy_port, service)
        logging.info(log_message)

        # Setting the proxy server and port
        set_proxy_command = ["/usr/sbin/networksetup", "-set{}proxy".format(netsetup_protocol), service, proxy,
                             proxy_port]
        try:
            enable_service_command = subprocess.check_output(set_proxy_command, shell=False)
        except:
            log_message = "Unable to set proxy {}".format(service)
            logging.error(log_message)

        # Add in the proxy exceptions
        log_message = "Setting proxy exceptions on {0}".format(service)
        logging.info(log_message)
        proxy_exceptions_command = ["/usr/sbin/networksetup", "-setproxybypassdomains", service, exceptions]
        try:
            enable_service_command = subprocess.check_output(proxy_exceptions_command, shell=False)
        except:
            log_message = "Unable to set proxy {}".format(service)
            logging.error(log_message)

    else:
        proxy_state_command = ["/usr/sbin/networksetup", "-set{}proxystate".format(netsetup_protocol), service,
                               proxy_state]
        log_message = "Turning {0} proxy {1}".format(protocol, proxy_state)
        logging.info(log_message)
        try:
            enable_service_command = subprocess.check_output(proxy_state_command, shell=False)
        except:
            log_message = "Unable to set proxy state to {}".format(proxy_state)
            logging.error(log_message)


def set_ipv6(state, service):
    if state == False:
        log_text = "off"
        command = "-setv6off"
    else:
        log_text = "on"
        command = "-setv6automatic"
    ipv6_state_command = ["/usr/sbin/networksetup", command, service]
    log_message = "Turning IPv6 {0} on {1}".format(log_text, service)
    logging.info(log_message)
    try:
        enable_service_command = subprocess.check_output(ipv6_state_command, shell=False)
    except:
        log_message = "Unable to set IPv6 state to {}".format(log_text)
        logging.error(log_message)


def set_autoproxy(state, service):
    if state == False:
        command = "off"
    else:
        command = "on"
    autoproxy_state_command = ["/usr/sbin/networksetup", "-setproxyautodiscovery", service, command]
    log_message = "Turning {0} proxy auto discovery on {1}".format(command, service)
    logging.info(log_message)
    try:
        enable_service_command = subprocess.check_output(autoproxy_state_command, shell=False)
    except:
        log_message = "Unable to set auto proxy discovery {}".format(command)
        logging.error(log_message)


def check_keys_present(expected_keys_list, given_keys_list):
    '''Compares two lists and returns a list of the difference'''
    given_keys = set(given_keys_list)
    expected_keys = set(expected_keys_list)
    if expected_keys == given_keys:
        # If they match then just return an empty set
        return []
    else:
        # Find out which column is missing and return a set of missing fields.
        return expected_keys.difference(given_keys)


# Main loop
def main():
    if (os.getuid() != 0):
        print "This script needs to be run as root"
        exit()

    # List the location keys that are required.
    required_keys = ["auto_proxy_discovery", "interface", "ipv6", "name", "proxy_exceptions"]
    starting_location = chomp(get_current_selected_location())

    # Setup logging
    logging.basicConfig(filename="/Library/Logs/create_locations.log", filemode="a", level=logging.DEBUG)
    logging.info("----------")
    logging.info("Starting create location script. {}".format(str(datetime.now())))
    logging.info("Starting location: {} ".format(starting_location))
    plist_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locations.plist")
    if os.path.isfile(plist_filename):
        try:
            locations_plist = readPlist(plist_filename)
        except:
            logging.critical("Loading plist failed")
            exit()
    else:
        log_message = "Can't load config file {}".format(plist_filename)
        logging.critical(log_message)
        exit()

    # Create new locations  
    if "active_locations" in locations_plist:
        for location in locations_plist["active_locations"]:

            # Check that all the required keys are there.
            missing_keys = check_keys_present(required_keys, location.keys())
            if len(missing_keys) > 0:
                if "name" in location:
                    logging.error(
                        "Can't create location {0}. It is missing the following keys : {1}".format(location["name"],
                                                                                                   ', '.join(
                                                                                                       missing_keys)))
                else:
                    logging.error("Can't create location. It doesn't even have a name")
                continue

            log_message = "Creating {}".format(location["name"])
            logging.info(log_message)
            create_location(location["name"])
            switch_location(location["name"])
            interface = get_actual_ethernet_service(location["interface"])
            disable_unnecessary_net_services(interface)
            if "http_proxy" in location:
                set_proxy(location["http_proxy"], location["http_proxy_port"], "http", interface,
                          location["proxy_exceptions"])
            if "https_proxy" in location:
                set_proxy(location["https_proxy"], location["https_proxy_port"], "https", interface,
                          location["proxy_exceptions"])
            if "ipv6" in location:
                set_ipv6(location["ipv6"], interface)
            set_autoproxy(location["auto_proxy_discovery"], interface)
    else:
        logging.info("No locations to create")


    # Remove obsolete locations
    if "obsolete_locations" in locations_plist:
        for obsolete_location in locations_plist["obsolete_locations"]:
            log_message = "Checking obsolete location {}".format(obsolete_location)
            logging.info(log_message)
            remove_location(obsolete_location)
    else:
        logging.info("No obsolete locations to remove")

    # Change location to the default
    if "default_location" in locations_plist:
        if locations_plist["default_location"] in get_current_locations():
            log_message = "Changing to default location: {}".format(locations_plist["default_location"])
            logging.info(log_message)
            switch_location(locations_plist["default_location"])
        else:
            log_message = "Unable to change to default location: {} it doesn't exist".format(
                locations_plist["default_location"])
            logging.error(log_message)
    else:
        logging.info("No default location specified. Attempting to change location to {}".format(starting_location))
        if starting_location in get_current_locations():
            switch_location(starting_location)
        else:
            current_location = chomp(get_current_selected_location())
            logging.info("Location {0} does not exist. Staying on {1}".format(starting_location, current_location))


if __name__ == '__main__':
    main()
