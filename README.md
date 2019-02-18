# Getting Started with OpenConfig
This testbed demonstrates a basic BGP peering deployment using 
OpenConfig data models.  It uses two ASBRs (`asbr1` and `asbr2`) and 
a Linux host acting as a controller where the automation scripts 
are executed.  The controller uses the following open source tools:

- Configuration management:  YANG development kit (YDK)
- Streaming telemetry: Pipeline and Kafka

Configuration changes are implemented in Python with YDK using the 
Openconfig interface and BGP models.  Operational validations are 
implemented in Python using a simple Kafka consumer that monitors 
interface and BGP session state using the respective OpenConfig models.

## Accessing Testbed Devices
The two ASBRs (`asbr1` and `asbr2`) and the controller share a common
management network.  They are reachable via ssh using the following
addresses:
- asbr1 - 198.18.1.11
- asbr2 - 198.18.1.12
- controller - 198.18.1.127
All devices use the same username/password credentials (admin/admin).

## Recommended Demo Execution
Deployment and withdrawal of peers is acomplished with two dedicated
scripts that take as input a peer configuration file in JSON format.
The structure of the peer configuration is arbitrary and is not based
on a specific data model. Both the deployment and withdrawal scripts 
are idempotent.

These are the contents of the peer configuration file:

```
admin@controller:~$ cd demo
admin@controller:demo$ cat peers.json 
{
  "asbr": {
    "name": "asbr1",
    "address": "198.18.1.11",
    "as": 65001
  },
  "peers": [{
    "address": "192.168.0.2",
    "as": 65002,
    "group": "EBGP",
    "interface": {
      "name": "GigabitEthernet0/0/0/0",
      "description": "Peering with AS65002",
      "address": "192.168.0.1",
      "netmask": 24
    }
  }]
}
admin@controller:demo$ 
```

The configuration file defines one peer for `asbr1`.  The peering details 
include the desired BGP and interface configuration. Note the peering 
device has been partially pre-configured with BGP global and peer group 
configuration, in addition to a basic route policy and appropriate 
telemetry sensors to stream BGP and interface state.  

Here is a sample execution of the deployment script using the peer
configuration file as input:

```
admin@controller:demo$ ./deploy_peers.py peers.json 
02:50:29.978416: Loading peer config ................................. [ OK ]
02:50:29.979221: Initializing connections ............................ [ OK ]
02:50:31.431766: Configure peer interface GigabitEthernet0/0/0/0 ..... [ OK ]
02:50:36.080111: Configure BGP peer 192.168.0.2 ...................... [ OK ]
admin@controller:demo$ 
```

Each task is confirmed with an `OK` if it is completed successfully.  For the
BGP and interface configuration tasks in particular, successful completion is
only reported if the proper operational state is validated using the 
BGP and interface state that `asbr1` streams. If validation can't be completed
after 60 seconds, the configuration task execution reports a `FAIL` completion.

Here is a sample execution of the withdrawal script using the peer 
configuration file as input:

```
admin@controller:demo$ ./withdraw_peers.py peers.json 
03:33:21.460814: Loading peer config ................................. [ OK ]
03:33:21.461946: Initializing connections ............................ [ OK ]
03:33:22.755176: Remove peer interface GigabitEthernet0/0/0/0 ........ [ OK ]
03:33:24.362452: Remove BGP peer 192.168.0.2 ......................... [ OK ]
admin@controller:demo$ 
```

The widthdrawal script does not make use of telemetry data for validation.

## Exploring Individual Tasks
Individual tasks can be executed with the following scripts:

```
config_bgp_peer.py
config_peer_interface.py
remove_bgp_peer.py
remove_peer_interface.py
validate_bgp_peer.py
validate_peer_interface.py
```

These scripts take their input from command line arguments.  They do not
make use of the peer configuration file (`peers.json`).  You can
experiment using different inputs and executing the scripts against any
of the two ASBRs. The file `demo-script.md` includes the invocation of 
each script with arguments equivalent to the data in the configuration
file (`peers.json`)

# Tool Chain Configuration
Pipeline, Kafka (including Zookeeper) run on separate docker containers:

```
admin@controller:demo$ docker ps
CONTAINER ID        IMAGE                           COMMAND                  CREATED             STATUS              PORTS                                        NAMES
111b9c10c0af        pipeline:1.0.0                  "/pipeline -log=/dat…"   7 weeks ago         Up 19 hours                                                      pipeline
7f28639cfa6b        confluent/kafka:0.10.0.0-cp1    "/usr/local/bin/kafk…"   7 weeks ago         Up 19 hours         0.0.0.0:9092->9092/tcp                       kafka
5ab7a5f9e685        confluent/zookeeper:3.4.6-cp1   "/usr/local/bin/zk-d…"   7 weeks ago         Up 19 hours         2888/tcp, 0.0.0.0:2181->2181/tcp, 3888/tcp   zookeeper
admin@controller:demo$
```

YDK is installed directly on the controller host:

```
admin@controller:demo$ pip3 list | grep ydk
ydk                   0.7.1                 
ydk-models-ietf       0.1.5                 
ydk-models-openconfig 0.1.5                 
admin@controller:demo$ 
```

You can experiment re-configuring the collector.  The configuration file (`pipeline.conf`) can be found at:

```
admin@controller:~$ ls demo/telemetry/pipeline/pipeline.conf 
demo/telemetry/pipeline/pipeline.conf
admin@controller:~$ 
```

Note that you need to restart the Pipeline container for the configuration changes to take effect.

Enjoy!
