# ISP topology
This folder contains a PoP-level(point of presence level) ISP topology dataset from the Rocketfuel project [(http://research.cs.washington.edu/networking/rocketfuel/)](http://research.cs.washington.edu/networking/rocketfuel/) and some experiment data generated based on the dataset. In the following, we describe the meaning and generation methodology of the individual subfolders/files -- `PoP-level ISP maps`, `topology figures`, `AS_links`, `nodes`, `ingress_egress`, `IGP` -- in this folder.

## PoP-level ISP maps
This folder contains 47 PoP-level ISP topology with inferred internal costs and link latency. Inside the folder, each subfolder is named with the format `x_y`. If `x` = `y`, the subfolder contains the internal PoP-level links of AS `x`, otherwise the subfolder contains the PoP-level interconnection links between AS `x` and AS `y`.

The methodology of how the topology is measured and how the weights are inferred are described in the paper [_Quantifying the Causes of Path Inflation_](https://ratul.org/papers/sigcomm2003-inflation.pdf).

Data source: [http://research.cs.washington.edu/networking/rocketfuel/maps/policy-dist.tar.gz]

## topology figures
This folder contains PoP-level ISP topology figures generated from the `PoP-level ISP maps` folder. The svg files can be displayed using mainstream browsers such as Firefox, Google Chrome, Safari etc.

## AS_links
This file contains AS links derived from the folder names of the subfolders under the `PoP-level ISP maps` folder, as each of the subfolders contains an `edge` file that gives either the interconnection links between a pair of AS, or the internal links of an AS. Some of the subfolders that do not contain any interconnection links are ignored.

Each line in the file has the format: \<AS 1>,\<AS 2>

## nodes
In a PoP-level ISP topology, each node is a location that an ISP has presence. This file assigns a node ID for each node in the PoP-level ISP topologies under the the `PoP-level ISP maps` folder. Please note that each node is uniquely identified by AS number and location.

Each line in the file has the format: \<ID>|\<AS number>|\<location>

## ingress_egress
This file provides the ingress nodes and egress nodes for each pair of neighboring ASes.

Each line in the file has the format: \<downstream AS>|\<upstream AS>|\<array of ingress nodes>|\<array of egress nodes>

**The role of downstream AS and upstream AS**: In each pair of neighboring ASes, the downstream AS is the AS that advertises routes to a certain prefix to the other AS, and the upstream AS is the AS that sends traffics to the routes that received from the downstream AS. As each AS may advocate prefixes to the other, the role of the downstream AS and the upstream AS depends on the route in question.

**Ingress and egress nodes**: Ingress nodes are the edge nodes in the downstream AS that connected to the upstream AS, and they are the nodes where the traffics from the upstream AS enter the network of the downstream AS. The egress nodes are the edge nodes in the downstream AS where the traffics from the upstream AS leave the network of the downstream AS.

## IGP
Inside the folder, there are IGP cost files for all the ISP topology in the `PoP-level ISP maps` folder. Each file is named by the corresponding AS number. The IGP cost is the path cost from an ingress node to an egress node.  We use the inferred link weight as the path length and run the Dijkstra algorithm to get the IGP cost for each pair of ingress and egress.

Each line in the files has the format: \<ingress>,\<egress>,\<cost>

Please note that for each ISP topology, that may be some ingress nodes that are disconnected from the graph and thus unable to reach any egress nodes. The IGP cost is set to 999 for the lines containing those ingress nodes.