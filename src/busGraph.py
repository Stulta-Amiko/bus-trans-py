import networkx as nx
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
import time
from util import findTerminal

if not (os.path.isdir('./data')):
    os.makedirs('./data/graph')
elif not(os.path.isdir('./data/graph')):
    os.mkdir('./data/graph')

if not(os.path.isfile('./data/graph/busGraph.edgelist')):
    G = nx.Graph() 
    f = open('./data/Express_Bus_Route_Detailed.csv','r')
    rdr = csv.reader(f)

    firstPass = 0

    for line in rdr:

        if firstPass == 0:
            firstPass += 1
        else:
            G.add_edge(line[2],line[4],weight=int(line[5]),relation='express')  


    f = open('./data/Intercity_Bus_Route_Detailed.csv','r')
    rdr = csv.reader(f)
    
    firstPass = 0

    for line in rdr:

        if firstPass == 0:
            firstPass += 1
        else:
            G.add_edge(line[2],line[4],weight=int(line[5]),relation='intercity')  


    f.close()

    nx.write_weighted_edgelist(G,'./data/graph/busGraph.edgelist')
else:
    G = nx.read_weighted_edgelist('./data/graph/busGraph.edgelist')

weight = nx.get_edge_attributes(G, 'weight')
relation = nx.get_edge_attributes(G, 'relation')

exitcode = 1

print('종료하시려면 출/도착지 입력시 0을 눌러주세요')

def peek(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return 0
    return 1
    
def csvlen(reader):
    csvindex = 0
    for item in reader:
        csvindex += 1
    return csvindex

while(exitcode == 1):

    cutoff = 0
    
    depart = findTerminal.find('출발')
    if depart == 0:
        exitcode = 0
    arrive = findTerminal.find('도착')
    if arrive == 0:
        exitcode = 0

    path = nx.all_shortest_paths(G, depart, arrive, weight='weight')
    length = nx.dijkstra_path_length(G,depart, arrive, weight='weight')
    simplePath = nx.all_simple_paths(G,depart,arrive,cutoff=cutoff)
    print(peek(simplePath))
    while not peek(simplePath):
        print(not peek(simplePath))
        if not peek(simplePath):
            cutoff += 1
            print(cutoff)
            simplePath = nx.all_simple_paths(G,depart,arrive,cutoff=cutoff)

    if cutoff < 2:
        cutoff += 1
        
    simplePath = nx.all_simple_paths(G,depart,arrive,cutoff=cutoff)

    result = list()

    for item in simplePath:
        indexpass = 0
        totalweight = 0
        route = list()
        if len(item) > 2:
            while indexpass <= len(item) - 2:
                weight = G.get_edge_data(item[indexpass],item[indexpass+1])
                totalweight += weight['weight']
                indexpass += 1
        else:
            weight = G.get_edge_data(item[0],item[1])
            totalweight += weight['weight']
        route.append(round(totalweight))
        for trip in item:
            route.append(trip)
        result.append(route)

    
    result = sorted(result,key=lambda triptime: triptime[0])

    nowHour = 0#datetime.now.hour
    nowMin = 0#datetime.now.minute

    newResult = list()

    for item in result:
        indexpass = 1
        eofpass = 0
        tripIndex = 0
        addweight = 0
        arrHour = 0
        arrMin = 0
        route = list()
        # 고속노선과 시외노선 구분하는거 추가 NAI인지 NAEK인지 구분 
        if len(item) > 3:
            while indexpass <= len(item) - 2:
                insidePass = 0
                try:
                    csvindex = 0
                    if os.path.isfile('./data/int_each/'+item[indexpass]+'/'+item[indexpass+1]+'_TimeTable.csv'):
                        f = open('./data/int_each/'+item[indexpass]+'/'+item[indexpass+1]+'_TimeTable.csv','r+')
                        f2 = open('./data/int_each/'+item[indexpass]+'/'+item[indexpass+1]+'_TimeTable.csv','r+')
                    else:
                        f = open('./data/exp_each/'+item[indexpass]+'/'+item[indexpass+1]+'_TimeTable.csv','r+')
                        f2 = open('./data/exp_each/'+item[indexpass]+'/'+item[indexpass+1]+'_TimeTable.csv','r+')

                    rdr = csv.reader(f)
                    rdr2 = csv.reader(f2)
                    listcsv = list(rdr)
                    csvindex = len(listcsv) 
                    

                    if csvindex < 2:
                        print('no timetable')
                        print(item[indexpass]+','+item[indexpass+1])
                        addweight += 7000
                        break

                    for line in rdr2:
                        if insidePass < 1:
                            insidePass += 1
                        else:
                            if indexpass < 2:
                                if int(line[3]) > nowHour or (int(line[3]) ==  nowHour and int(line[4]) > nowMin):
                                    arrHour = int(line[7])
                                    arrMin = int(line[8])
                                    indexpass += 1
                                    break

                            else:
                                eofpass += 1
                                if eofpass > 50:
                                    print('eof detected')
                                    indexpass += 100
                                    addweight += 7000
                                    break
                                if int(line[3]) > arrHour or (int(line[3]) ==  arrHour and int(line[4]) > arrMin):
                                    addweight += (int(line[3]) - arrHour)*60 + int(line[4]) - arrMin
                                    arrHour = int(line[7])
                                    arrMin = int(line[8])
                                    indexpass += 1
                                    break
                        

                except:
                    print('no directory... addweight += 7000... 사용불가노선')
                    addweight += 7000
                    indexpass += 1
                    break

            if item[0]+addweight < 7000:
                route = [item[0]+addweight,item[1],item[2],item[3],addweight]
                newResult.append(route)
        else:
            route = item
            newResult.append(route) 

    newResult = sorted(newResult,key=lambda triptime: triptime[0])
    for item in newResult:
        print(item)
    

    '''
    for index,route in enumerate(path):
        if len(path) - 1 > index:
            print(path[index]+'-'+path[index+1])
    tripHour = length // 60
    tripMin  = length % 60
    if length < 1:
        print('소요시간 ' + str(int(tripMin)) + '분')
    else:
        print('소요시간 ' + str(int(tripHour)) + '시간 ' +str(int(tripMin)) + '분') 
    print("Path length: ", length)

'''