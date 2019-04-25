import os, sys, re

pyPath = os.path.dirname(os.path.abspath(__file__))
allFolders = os.listdir(pyPath)
linkFolders = [e for e in allFolders if re.match('[1-9]{1,}_[1-9]{1,}', e)]

AS = []
ASlinks = []
allASlinks = []
for e in linkFolders:
    ASNum = e.split('_')
    if(int(ASNum[0]) != int(ASNum[1])):
        ef = open(os.path.join(pyPath, e+'/edges'))
        for l in ef:
            ASlinks.append((int(ASNum[0]),int(ASNum[1])))
            break
        ef.close()
    else:
        AS.append(int(ASNum[0]))
AS.sort()
ASlinks.sort()
f = open('AS_links', 'w')
for a in ASlinks:
    f.write(str(a[0])+','+str(a[1])+'\n')
f.close()
f = open(os.path.join(pyPath,'cycles_combined.txt'), 'r')
for l in f:
    ASNum = l.split(',')
    allASlinks.append((int(ASNum[0]), int(ASNum[1])))
f.close()

overlapLinks = []
missedLinks = []

for (s,d) in ASlinks:
    if ((s,d) in allASlinks) or ((d,s) in allASlinks):
        overlapLinks.append((s,d))
    else:
        missedLinks.append((s,d))
print len(overlapLinks), len(missedLinks)


