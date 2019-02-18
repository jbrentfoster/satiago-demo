#!/usr/bin/env python3
#
# Copyright 2016 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Create configuration for peer interface.

usage: config_peer_interface.py [-h] [-v] name description address netmask device

positional arguments:
  name           interface name
  description    interfaces description
  address        interface address
  netmask        interface network mask
  device         NETCONF device (ssh://user:password@host:port)

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  print debugging messages
"""

import argparse
import urllib.parse

from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
from ydk.models.openconfig import openconfig_interfaces as oc_interfaces
from ydk.models.ietf import iana_if_type
import logging


def config_peer_interface(interfaces, name, description, address, netmask):
    """Add config data to interfaces object."""
    # configure interface
    interface = interfaces.Interface()
    interface.name = name
    interface.config.name = name
    interface.config.type = iana_if_type.Ethernetcsmacd()
    interface.config.description = description
    interface.config.enabled = True

    # configure ip subinterface
    subinterface = interface.subinterfaces.Subinterface()
    subinterface.index = 0
    subinterface.config.index = 0
    address_ = subinterface.ipv4.addresses.Address()
    address_.ip = address
    address_.config.ip = address
    address_.config.prefix_length = netmask
    subinterface.ipv4.addresses.address.append(address_)
    interface.subinterfaces.subinterface.append(subinterface)
    interfaces.interface.append(interface)


if __name__ == "__main__":
    """Execute main program."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", 
                        help="print debugging messages",
                        action="store_true")
    parser.add_argument("name",
                        help="interface name")
    parser.add_argument("description",
                        help="interfaces description")
    parser.add_argument("address",
                        help="interface address")
    parser.add_argument("netmask",
                        help="interface network mask")
    parser.add_argument("device",
                        help="NETCONF device (ssh://user:password@host:port)")
    args = parser.parse_args()
    device = urllib.parse.urlparse(args.device)

    # log debug messages if verbose argument specified
    if args.verbose:
        logger = logging.getLogger("ydk")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(("%(asctime)s - %(name)s - "
                                      "%(levelname)s - %(message)s"))
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # create NETCONF provider
    provider = NetconfServiceProvider(address=device.hostname,
                                      port=device.port,
                                      username=device.username,
                                      password=device.password,
                                      protocol=device.scheme)
    # create CRUD service
    crud = CRUDService()

    # interface configuration
    interfaces = oc_interfaces.Interfaces()
    config_peer_interface(interfaces, args.name, args.description, args.address, args.netmask)

    # create configuration on NETCONF device
    crud.create(provider, interfaces)

    exit()
# End of script
