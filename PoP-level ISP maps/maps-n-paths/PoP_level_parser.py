import os, sys, re
from igraph import Graph

pyPath = os.path.dirname(os.path.abspath(__file__))
edgeFolders = os.listdir(pyPath)

class Topo( object ):

    def __init__( self, *args, **params ):
        """Topo object.
           Optional named parameters:
           hinfo: default host options
           sopts: default switch options
           lopts: default link options
           calls build()"""
        self.g = Graph(directed=True)
        self.hopts = params.pop( 'hopts', {} )
        self.sopts = params.pop( 'sopts', {} )
        self.lopts = params.pop( 'lopts', {} )
        # ports[src][dst][sport] is port on dst that connects to src
        self.ports = {}
        self.build( *args, **params )

    def build( self, *args, **params ):
        "Override this method to build your topology."
        pass

    def addNode( self, name, **opts ):
        """Add Node to graph.
           name: name
           opts: node options
           returns: node name"""
        self.g.add_vertex( name, **opts )
        return name

    def addHost( self, name, **opts ):
        """Convenience method: Add host to graph.
           name: host name
           opts: host options
           returns: host name"""
        if not opts and self.hopts:
            opts = self.hopts
        return self.addNode( name, isSwitch=False, **opts )

    def addSwitch( self, name, **opts ):
        """Convenience method: Add switch to graph.
           name: switch name
           opts: switch options
           returns: switch name"""
        if not opts and self.sopts:
            opts = self.sopts
        return self.addNode( name, isSwitch=True, **opts )

    def addLink( self, node1, node2, port1=None, port2=None, key=None, **opts ):
        """node1, node2: nodes to link together
           port1, port2: ports (optional)
           opts: link options (optional)
           key: useless, kept for compatibility with mininet"""
        if not opts and self.lopts:
            opts = self.lopts
        port1, port2 = self.addPort( node1, node2, port1, port2 )
        opts = dict( opts )
        opts.update( node1=node1, node2=node2, port1=port1, port2=port2 )
        self.g.add_edge(node1, node2, **opts)

    def nodes( self, sort=True ):
        """Return a list of nodes in graph"""
        nodes = self.g.vs["name"]
        if sort:
            nodes.sort()
        return nodes

    def isSwitch( self, n ):
        """Return true if node is a switch."""
        return self.g.vs.find(name=n)['isSwitch']

    def switches( self, sort=True ):
        """Return a list of switches."""
        #return [ n for n in self.nodes() if self.isSwitch( n ) ]
        switches = self.g.vs.select(isSwitch=True)["name"]
        if sort:
            switches.sort()
        return switches

    def hosts( self, sort=True ):
        """Return a list of hosts."""
        hosts =  self.g.vs.select(isSwitch=False)["name"]
        if sort:
            hosts.sort()
        return hosts

    def links( self, sort=False, withKeys=False, withInfo=False ):
        """Return a list of links
           sort: sort links alphabetically, preserving (src, dst) order
           withKeys: return link keys
           withInfo: return link info
           returns: list of ( src, dst [,key, info ] )"""
        
        if withKeys:
            if withInfo:
                links = [(self.g.vs[e[0]]["name"], self.g.vs[e[1]]["name"], e, self.g.es[self.g.get_eid(e[0],e[1])].attributes()) for e in self.g.get_edgelist()]
            else:
                links = [(self.g.vs[e[0]]["name"], self.g.vs[e[1]]["name"], e) for e in self.g.get_edgelist()]
        else:
            if withInfo:
                links = [(self.g.vs[e[0]]["name"], self.g.vs[e[1]]["name"], self.g.es[self.g.get_eid(e[0],e[1])].attributes()) for e in self.g.get_edgelist()]
            else:
                links = [(self.g.vs[e[0]]["name"], self.g.vs[e[1]]["name"]) for e in self.g.get_edgelist()]
        if sort:
            links.sort()
        return links

    def addPort( self, src, dst, sport=None, dport=None ):
        """Generate port mapping for new edge.
            src: source switch name
            dst: destination switch name"""
        # Initialize if necessary
        ports = self.ports
        ports.setdefault( src, {} )
        ports.setdefault( dst, {} )
        # New port: number of outlinks + base
        if sport is None:
            src_base = 1 if self.isSwitch( src ) else 0
            sport = len( ports[ src ] ) + src_base
        if dport is None:
            dst_base = 1 if self.isSwitch( dst ) else 0
            dport = len( ports[ dst ] ) + dst_base
        ports[ src ][ sport ] = ( dst, dport )
        ports[ dst ][ dport ] = ( src, sport )
        return sport, dport

    def port( self, src, dst ):
        """Get port numbers.
            src: source switch name
            dst: destination switch name
            returns: tuple (sport, dport), where
                sport = port on source switch leading to the destination switch
                dport = port on destination switch leading to the source switch"""
        e = self.g.es.find(node1_in=[src,dst], node2_in=[src,dst])
        (sport, dport) = (e["port1"], e["port2"]) if e["node1"] == src else (e["port2"], e["port1"])
        return (sport, dport)

    def _linkEntry( self, src, dst, key=None ):
        """Helper function: return link entry and key."""
        entry = self.g.es.find(node1_in=[src,dst], node2_in=[src,dst]).attributes()
        if key is None:
            key = min( entry )
        return entry, key

    def linkInfo( self, src, dst, key=None ):
        """Return link metadata dict
           We use simple graph, a (src,dst) tuple maps to one edge if exists."""
        #entry, key = self._linkEntry( src, dst, key )
        return self.g.es.find(node1_in=[src,dst], node2_in=[src,dst]).attributes()

    def setlinkInfo( self, src, dst, info, key=None ):
        """Set link metadata dict"""
        edgeIdx = self.g.es.find(node1_in=[src,dst], node2_in=[src,dst]).index
        for k in info.keys():
            self.g.es[edgeIdx][k] = info[k]

    def nodeInfo( self, name ):
        """Return metadata (dict) for node"""
        info = self.g.vs.find(name_eq=name).attributes()
        info.pop('name', None)#the name attribute will cause multiple value assigment for a key word argument 'name' in Mininet, it's redundant anyway.
        return info

    def setNodeInfo( self, name, info ):
        "Set metadata (dict) for node"
        self.g.node[ name ] = info
        vertexIdx = self.g.vs.find(name_eq=name).index
        for k in info.keys():
            self.g.vs[vertexIdx][k] = info[k]

class PoPISPTopo(Topo):
    def build(self, k, **_opts):
        self.ASNum = int(k)
        nodes = {}
        edges = {}

        ## parse internal links
        # parse link
        internalLinks = open(os.path.join(pyPath, str(k)+'_'+str(k)+'/edges'))
        for line in internalLinks:
            # line format: ASN:City -> ASN:City observed_times
            nodeNames = line.split(' -> ')
            node1 = nodeNames[0]
            node2 = nodeNames[1].rsplit(' ', 1)[0]
            for node in (node1, node2):
                if node not in nodes.keys():
                    city = node.split(':')[1]
                    nodes[node] = {'ASNum': self.ASNum, 'city':city, 'border':False}
            if (node2, node1) not in edges.keys():
                edges[(node1, node2)] = {'internal':True}
        internalLinks.close()

        # parse link latency
        linkLatency = open(os.path.join(pyPath, str(k)+'_'+str(k)+'/edges.lat'))
        for line in linkLatency:
            # line format: ASN:City -> ASN:City latency_in_ms
            nodeNames = line.split(' -> ')
            node1 = nodeNames[0]
            node2 = nodeNames[1].rsplit(' ', 1)[0]
            if (node1, node2) in edges.keys():
                latency = float(nodeNames[1].rsplit(' ', 1)[1])
                edges[(node1, node2)]['latency'] = latency
        linkLatency.close()

        # parse link weight
        linkWeight = open(os.path.join(pyPath, str(k)+'_'+str(k)+'/edges.wt'))
        for line in linkWeight:
            # line format: ASN:City -> ASN:City weight
            nodeNames = line.split(' -> ')
            node1 = nodeNames[0]
            node2 = nodeNames[1].rsplit(' ', 1)[0]
            if (node1, node2) in edges.keys():
                weight = float(nodeNames[1].rsplit(' ', 1)[1])
                edges[(node1, node2)]['weight'] = weight
        linkWeight.close()

        ## parse external links
        externalLinkFolders = [e for e in edgeFolders if (re.match(str(self.ASNum)+'_[0-9]*', e) and e != str(self.ASNum)+'_'+str(self.ASNum))]
        for f in externalLinkFolders:
            # parse link
            externalLinks = open(os.path.join(pyPath, f+'/edges'))
            for line in externalLinks:
                nodeNames = line.split(' -> ')
                node1 = nodeNames[0]
                node2 = nodeNames[1].rsplit(' ', 1)[0]
                for node in (node1, node2):
                    ASNum = int(node.split(':')[0])
                    city = node.split(':')[1]
                    nodes[node] = {'ASNum':ASNum, 'city':city, 'border': True}
                edges[(node1, node2)] = {'internal':False}
            externalLinks.close()

            # parse link latency
            linkLatency = open(os.path.join(pyPath, f+'/edges.lat'))
            for line in linkLatency:
                nodeNames = line.split(' -> ')
                node1 = nodeNames[0]
                node2 = nodeNames[1].rsplit(' ', 1)[0]
                latency = float(nodeNames[1].rsplit(' ', 1)[1])
                edges[(node1, node2)]['latency'] = latency
            linkLatency.close()

        for node in nodes.keys():
            self.addSwitch(node, **nodes[node])
        for edge in edges:
            self.addLink(edge[0], edge[1], **edges[edge])

class PoPISPTopoPair(Topo):
    def build(self, downstreamAS, upstreamAS, **_opts):
        self.downstreamAS = int(downstreamAS)
        self.upstreamAS = int(upstreamAS)
        nodes = {}
        edges = {}

        ## parse internal links
        # parse link
        for k in (self.downstreamAS, self.upstreamAS):
            internalLinks = open(os.path.join(pyPath, str(k)+'_'+str(k)+'/edges'))
            for line in internalLinks:
                # line format: ASN:City -> ASN:City observed_times
                nodeNames = line.split(' -> ')
                node1 = nodeNames[0]
                node2 = nodeNames[1].rsplit(' ', 1)[0]
                for node in (node1, node2):
                    if node not in nodes.keys():
                        city = node.split(':')[1]
                        nodes[node] = {'ASNum': k, 'city':city, 'border':False}
                if (node2, node1) not in edges.keys():
                    edges[(node1, node2)] = {'internal':True}
            internalLinks.close()

            # parse link latency
            linkLatency = open(os.path.join(pyPath, str(k)+'_'+str(k)+'/edges.lat'))
            for line in linkLatency:
                # line format: ASN:City -> ASN:City latency_in_ms
                nodeNames = line.split(' -> ')
                node1 = nodeNames[0]
                node2 = nodeNames[1].rsplit(' ', 1)[0]
                if (node1, node2) in edges.keys():
                    latency = float(nodeNames[1].rsplit(' ', 1)[1])
                    edges[(node1, node2)]['latency'] = latency
            linkLatency.close()

            # parse link weight
            linkWeight = open(os.path.join(pyPath, str(k)+'_'+str(k)+'/edges.wt'))
            for line in linkWeight:
                # line format: ASN:City -> ASN:City weight
                nodeNames = line.split(' -> ')
                node1 = nodeNames[0]
                node2 = nodeNames[1].rsplit(' ', 1)[0]
                if (node1, node2) in edges.keys():
                    weight = float(nodeNames[1].rsplit(' ', 1)[1])
                    edges[(node1, node2)]['weight'] = weight
            linkWeight.close()

        ## parse peering links
        peeringLinks = open(os.path.join(pyPath,'{}_{}'.format(self.downstreamAS, self.upstreamAS), 'edges'))
        # parse link
        for line in peeringLinks:
            nodeNames = line.split(' -> ')
            node1 = nodeNames[0]
            node2 = nodeNames[1].rsplit(' ', 1)[0]
            for node in (node1, node2):
                nodes[node]['border'] = True
            edges[(node1, node2)] = {'internal':False}
        peeringLinks.close()

        # parse link latency
        linkLatency = open(os.path.join(pyPath,'{}_{}'.format(self.downstreamAS, self.upstreamAS), 'edges.lat'))
        for line in linkLatency:
            nodeNames = line.split(' -> ')
            node1 = nodeNames[0]
            node2 = nodeNames[1].rsplit(' ', 1)[0]
            latency = float(nodeNames[1].rsplit(' ', 1)[1])
            edges[(node1, node2)]['latency'] = latency
        linkLatency.close()

        for node in nodes.keys():
            self.addSwitch(node, **nodes[node])
        for edge in edges:
            self.addLink(edge[0], edge[1], **edges[edge])

g1 = PoPISPTopo(3)
g2 = PoPISPTopoPair(1,3)
print len(g1.g.es)
print len(g2.g.es)