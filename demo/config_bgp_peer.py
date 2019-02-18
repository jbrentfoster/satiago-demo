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
Create configuration for BGP peer.

usage: config_bgp_peer.py [-h] [-v] local_as peer_address peer_as device

positional arguments:
  local_as       local autonomous system
  peer_address   peer address
  peer_as        peer autonomous system
  peer_group     peer group
  device         NETCONF device (ssh://user:password@host:port)

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  print debugging messages
"""

import argparse
import urllib.parse

from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
from ydk.models.openconfig import openconfig_bgp as oc_bgp
import logging


def config_bgp_peer(bgp, local_as, peer_address, peer_as, peer_group):
    """Add config data to bgp object."""
    # configure global bgp
    bgp.global_.config.as_ = local_as

    # configure neighbor
    neighbor = bgp.neighbors.Neighbor()
    neighbor.neighbor_address = peer_address
    neighbor.config.neighbor_address = peer_address
    neighbor.config.peer_as = peer_as
    neighbor.config.peer_group = peer_group
    bgp.neighbors.neighbor.append(neighbor)


if __name__ == "__main__":
    """Execute main program."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", 
                        help="print debugging messages",
                        action="store_true")
    parser.add_argument("local_as",
                        help="local autonomous system")
    parser.add_argument("peer_address",
                        help="peer address")
    parser.add_argument("peer_as",
                        help="peer autonomous system")
    parser.add_argument("peer_group",
                        help="peer group")
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

    # BGP configuration
    bgp = oc_bgp.Bgp()
    config_bgp_peer(bgp, args.local_as, args.peer_address, args.peer_as, args.peer_group)

    # create configuration on NETCONF device
    crud.create(provider, bgp)

    exit()
# End of script
