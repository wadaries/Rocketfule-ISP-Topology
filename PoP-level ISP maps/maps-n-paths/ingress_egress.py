import os, sys, re
from PoP_level_parser import PoPISPTopo
pyPath = os.path.dirname(os.path.abspath(__file__))
allFolders = os.listdir(pyPath)
linkFolders = [e for e in allFolders if re.match('[1-9]{1,}_[1-9]{1,}', e)]

ASes = []
ASlinks = []
for e in linkFolders:
    ASNum = e.split('_')
    if(int(ASNum[0]) == int(ASNum[1])):
        ASes.append(int(ASNum[0]))
    else:
        ASlinks.append((int(ASNum[0]), int(ASNum[1])))
ASes.sort()
f = open('AS', 'w')
for a in ASes:
    f.write(str(a)+'\n')
f.close()
# take only AS links between ASes that we have complete topology information
ASlinks = [l for l in ASlinks if l[0] in ASes and l[1] in ASes]
ASlinks.sort()


nodesIdDict = {}
f = open("nodes")
for l in f:
    temp = l.split('|', 1)
    temp[1] = temp[1].strip('\n')
    nodesIdDict[temp[1].replace('|',':')] = int(temp[0])
f.close()

WiserASlinks = []
f = open('ingress_egress', 'w')
lf = open('AS_links', 'w')
plf = open('peering_links', 'w')
for a in ASes:
    peeringASes = [e[1] for e in ASlinks if e[0] == a]
    topo = PoPISPTopo(a)
    borderNodes = [n["name"] for n in topo.g.vs.select(ASNum=a, border=True)]
    for p in peeringASes:
        # All the nodes that connected to p are considered as ingress nodes.
        peeringNodes = topo.g.vs.select(ASNum=p)
        ingress = []
        for n in peeringNodes:
            peeringlinkIdx = topo.g.incident(n.index)
            for l in peeringlinkIdx:
                if topo.g.es[l].source == n.index:
                    if topo.g.vs[topo.g.es[l].target]["name"] not in ingress:
                        ingress.append(topo.g.vs[topo.g.es[l].target]["name"]) 
                    plf.write(str(a)+','+str(p)+','+str(nodesIdDict[topo.g.vs[topo.g.es[l].target]["name"]])+','+str(nodesIdDict[topo.g.vs[topo.g.es[l].source]["name"]])+'\n')
                else:
                    if topo.g.vs[topo.g.es[l].source]["name"] not in ingress:
                        ingress.append(topo.g.vs[topo.g.es[l].source]["name"])
                    plf.write(str(a)+','+str(p)+','+str(nodesIdDict[topo.g.vs[topo.g.es[l].source]["name"]])+','+str(nodesIdDict[topo.g.vs[topo.g.es[l].target]["name"]])+'\n')
        ingress = [nodesIdDict[n] for n in ingress]
        ingress.sort()
        '''
        # All the border nodes that connected to peering ASes except for p are considered as egress nodes.
        borderNodes = topo.g.vs.select(ASNum_notin=[a, p])
        egress = []
        for n in borderNodes:
            peeringlinkIdx = topo.g.incident(n.index)
            for l in peeringlinkIdx:
                if topo.g.es[l].source == n.index:
                    if topo.g.vs[topo.g.es[l].target]["name"] not in egress:
                        egress.append(topo.g.vs[topo.g.es[l].target]["name"]) 
                else:
                    if topo.g.vs[topo.g.es[l].source]["name"] not in egress:
                        egress.append(topo.g.vs[topo.g.es[l].source]["name"])
        '''
        egress = [nodesIdDict[n] for n in borderNodes if nodesIdDict[n] not in ingress]
        egress.sort()
        if len(ingress) > 1 and len(egress) > 0:
            f.write(str(a)+'|'+str(p)+'|'+str(ingress).replace('[','{').replace(']','}')+'|'+str(egress).replace('[','{').replace(']','}')+'\n')
            lf.write(str(a)+','+str(p)+'\n')
            WiserASlinks.append((a,p))
f.close()
lf.close()
plf.close()