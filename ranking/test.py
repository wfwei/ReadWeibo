# !/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy.sparse import *
from scipy import *
import networkx as nx
import numpy as np
import sys, os


G=nx.Graph()
G.add_weighted_edges_from([
    (1,2,.5), (1,4,.75), (1,5,.5),
    (2,3,.5), (2,6,.75), (2,5,.5),
    (3,4,.5), (3,6,.75), (3,7,.5),
    (4,5,.5), (4,7,.75), (1,5,.5),
    ])
#nx.draw(G)
#plt.show()

nod=0; inc=0; outc=0
for i in range(6):
    nod += 1
    nod = i+1
    for nei in G[nod]:
        if u'visited' in G[nod][nei]:
            outc -= 1
            inc += 1
        else:
            outc += 1
            G[nod][nei]['visited'] = True

    print u'current node:%s\t status<%s/%s>' % (nod, inc, outc)



sys.exit(0)

mt = [[0.0,2.0,3.0,0.0],
      [2.0,0.0,1.0,0.0],
      [3.0,1.0,0.0,4.0],
      [0.0,0.0,4.0,0.0]]

W = csr_matrix((4,4))
D = csr_matrix((4,4))

W[0,1]=2;W[1,0]=2;
W[0,2]=3;W[2,0]=3
W[1,2]=1;W[2,1]=1
W[3,2]=1;W[2,3]=4

n=4
_sum = W.sum(1)
for _i in range(n):
    if _sum[_i,0] != 0:
        D[_i, _i] = _sum[_i,0]**(-0.5)

S = D.dot(W).dot(D)

print '\nW:\n', W.todense()
print '\nD:\n', D.todense()
print '\nS:\n', S.todense()


f = np.zeros((4,1))
y = np.array([[1,0,1,0]]).T
alpha = 0.15

for _iter in range(30):
    f = alpha*S.dot(f) + (1-alpha)*y

print f
sys.exit(0)

os.system('clear')
print u"running %s" % ' '.join(sys.argv)

G = nx.Graph()
G.add_node('wfw', tp='man')
G.add_node('fengwei', tp='man')
G.add_node(u'峰伟', tp='man')
G.add_node('Genius', tp='word')

G.add_edge('wfw', u'峰伟', weight=1.0)
G.add_edge('wfw', 'Genius', weight=0.99999)


nx.write_adjlist(G, sys.stdout, comments='#', delimiter=' ', encoding='utf-8')


print '------------'

#visit edges
for edge in G.edges():
    print edge


sys.exit(0)

print 'nodes:%d\tedges:%d' % (G.number_of_nodes(), G.number_of_edges())

# visit node
print G.node[u'wfw']['tp']

#visit enighbors
print G[u'wfw']
print G.neighbors(u'wfw')

print len(G)

# label an id to each node
st = 0
for key in G.nodes():
    G.node[key]['id'] = st
    st += 1
for key, nod in G.nodes(data=True):
    print key, nod



for key, node in G.nodes(data=True):
    print key, node
