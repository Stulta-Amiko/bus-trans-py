import os
import csv
import networkx as nx

#그래프 생성과정 

def makeGraph():
    if not (os.path.isdir('/Users/user/Desktop/mern/pyparse/busroute/src/data')):
        os.makedirs('/Users/user/Desktop/mern/pyparse/busroute/src/data/graph')
    elif not(os.path.isdir('/Users/user/Desktop/mern/pyparse/busroute/src/data/graph')):
        os.mkdir('/Users/user/Desktop/mern/pyparse/busroute/src/data/graph')

    if not(os.path.isfile('/Users/user/Desktop/mern/pyparse/busroute/src/data/graph/busGraph.edgelist')):
        G = nx.Graph() 
        f = open('/Users/user/Desktop/mern/pyparse/busroute/src/data/Express_Bus_Route_Detailed.csv','r')
        rdr = csv.reader(f)

        firstPass = 0

        for line in rdr:

            if firstPass == 0:
                firstPass += 1
            else:
                G.add_edge(line[2],line[4],weight=int(line[5]),relation='express')  


        f = open('/Users/user/Desktop/mern/pyparse/busroute/src/data/Intercity_Bus_Route_Detailed.csv','r')
        rdr = csv.reader(f)
        
        firstPass = 0

        for line in rdr:

            if firstPass == 0:
                firstPass += 1
            else:
                G.add_edge(line[2],line[4],weight=int(line[5]),relation='intercity')  

        f.close()

        nx.write_weighted_edgelist(G,'/Users/user/Desktop/mern/pyparse/busroute/src/data/graph/busGraph.edgelist')
    else:
        G = nx.read_weighted_edgelist('/Users/user/Desktop/mern/pyparse/busroute/src/data/graph/busGraph.edgelist')

    return G