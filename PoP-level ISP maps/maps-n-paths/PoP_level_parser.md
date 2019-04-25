# Rocketfuel PoP-level ISP topology parser

The PoP_level_parser.py contains two class --- PoPISPTopo and PoPISPTopoPair --- that parse the PoP-leve ISP dataset from [Rocketfuel](http://research.cs.washington.edu/networking/rocketfuel/). This parser stores the parsed topology in a Topo class which is just a wrapper of the Graph object from the [igraph-python](http://igraph.org/python/) library. The wrapper is adapted from the Mininet's [topology library](https://github.com/mininet/mininet/blob/26b395996806a31890951f08e456ccfa89c3ec8e/mininet/topo.py#L99).

Please note that the links in the PoP-level ISP topology dataset are both directional and symmetric, which means each link has two edges with the same attributes (weight and latency) going to the opposite direction. Since the link is symmetric, this parser stores the topology as a undirected graph.

## Vertex attributes

The vertex of the Graph object has the following attributes:

* name: The name of the node.

* ASNum: Which AS this node belongs to.

* isSwitch: A boolean indicates whether the node is a switch or not.

* isHost: A boolean indicates whether the node is a host or not.

* border: A boolean indicates whether the node is a border node or not. For example, is a node is connected to a neighboring AS, then the attribute is true.

## Edge attributes

The edge of the Graph object has the following attributes:

* internal: A boolean indicate whether the edge is an internal link of the ISP.

* weight: The cost of the link in float type.

* latency: The latency of the link in float type. The unit is millisecond.

* node1: One of the end node.

* node2: One of the end node.

* port1: The port number of the node 1 that this link is connected to.

* port2: The port number of the node 2 that this link is connected to.

## PoPISPTopo

Given an AS number, this class loads the PoP-level ISP topology of the AS with the internal costs and link latencies. The costs and latencies are stored as the attributes of the edges. Note that the topology also contains the AS's peering links with its neighbors, so the loaded ISP topology contains nodes that belong to its neighbors.

For example, the following codes loads the PoP-level topology of AS 1221, and get all the edge nodes:

```Python
tp = PoPISPTopo(3)
edgeNodes = [n["name"] for n in tp.g.vs.select(ASNum=3, border=True)]
```

## PoPISPTopoPair

Given a pair of downstream AS and upstream AS, this class loads their PoP-level ISP topology and the peering links. The internal costs and latencies are also loaded and stored as the attributes of the edges. But unlike the PoPISPTopo class, only the nodes belong to the two ASes are loaded, which means the topology class does not contain the peering links with any other neighboring ASes.

For example, the following codes loads the PoP-level topology of AS 1 and AS 3, and get all the nodes in AS 1:

```Python
tp = PoPISPTopoPair(1, 3)
edgeNodes = [n["name"] for n in tp.g.vs.select(ASNum=3)]
```