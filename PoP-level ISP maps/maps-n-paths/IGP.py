import os, sys, re
from PoP_level_parser import PoPISPTopo

pyPath = os.path.dirname(os.path.abspath(__file__))
allFolders = os.listdir(pyPath)
linkFolders = [e for e in allFolders if re.match('[1-9]{1,}_[1-9]{1,}', e)]
'''
nodes = {}
for e in linkFolders:
    edges = open(os.path.join(pyPath, e+'/edges'))
    for line in edges:
        # line format: ASN:City -> ASN:City observed_times
        nodeNames = line.split(' -> ')
        node1 = nodeNames[0]
        temp = node1.split(':')
        ASNum = int(temp[0])
        temp = temp[1].rsplit(', ', 1)
        if len(temp) == 2:
            city = temp[0]
            state = temp[1]
        else:
            city = temp[0]
            state = 'z'
        node1key = (ASNum, state, city)
        node2 = nodeNames[1].rsplit(' ', 1)[0]
        temp = node2.split(':')
        ASNum = int(temp[0])
        temp = temp[1].rsplit(', ', 1)
        if len(temp) == 2:
            city = temp[0]
            state = temp[1]
        else:
            city = temp[0]
            state = 'z'
        node2key = (ASNum, state, city)
        if node1key not in nodes.keys():
            nodes[node1key] = node1
        if node2key not in nodes.keys():
            nodes[node2key] = node2
    edges.close()
'''
nidDict = {}
f = open('nodes')
for l in f:
    temp = l.split('|',1)
    temp[1] = temp[1].replace('|',':')
    nidDict[temp[1].strip('\n')] = int(temp[0])
f.close()
    
ASes = []
for e in linkFolders:
    ASNums = e.split('_')
    if (int(ASNums[0]) == int(ASNums[1])):
        ASes.append(int(ASNums[0]))
ASes.sort()

f = open('allIGP', 'w')
for a in ASes:
    topo = PoPISPTopo(a)
    #topo.g.write_svg('AS'+str(a)+'.svg', labels="name", width=1920, height=1080, font_size="10", vertex_size=10)
    evs = topo.g.vs.select(ASNum_ne = a)
    topo.g.delete_vertices(evs)
    vs = topo.g.vs.select(border=True)
    idx = [v.index for v in vs]
    src = [v["name"] for v in vs]
    dst = src
    costMatrix = topo.g.shortest_paths_dijkstra(source=idx, target=idx, weights="weight")
    sCnt = 0
    for s in src:
        srcID = str(nidDict[s])
        dCnt = 0
        costVector = costMatrix[sCnt]
        for d in dst:
            dstID = str(nidDict[d])
            cost = costVector[dCnt]
            if cost == float('inf'):
                cost = 999
            #if cost > 0 and cost < 999:
            f.write(str(a)+','+srcID+','+dstID+','+str(cost)+'\n')
            dCnt = dCnt + 1
        sCnt = sCnt+1
f.close()





