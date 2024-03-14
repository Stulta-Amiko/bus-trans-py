import networkx as nx
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
import time
from util import findTerminal

if not (os.path.isdir('src/data')):
    os.makedirs('src/data/graph')
elif not(os.path.isdir('src/data/graph')):
    os.mkdir('src/data/graph')

if not(os.path.isfile('src/data/graph/busGraph.edgelist')):
    G = nx.Graph() 
    f = open('src/data/Express_Bus_Route_Detailed.csv','r')
    rdr = csv.reader(f)

    firstPass = 0

    for line in rdr:

        if firstPass == 0:
            firstPass += 1
        else:
            G.add_edge(line[2],line[4],weight=int(line[5]),relation='express')  


    f = open('src/data/Intercity_Bus_Route_Detailed.csv','r')
    rdr = csv.reader(f)
    
    firstPass = 0

    for line in rdr:

        if firstPass == 0:
            firstPass += 1
        else:
            G.add_edge(line[2],line[4],weight=int(line[5]),relation='intercity')  


    f.close()

    nx.write_weighted_edgelist(G,'src/data/graph/busGraph.edgelist')
else:
    G = nx.read_weighted_edgelist('src/data/graph/busGraph.edgelist')

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

    nowHour = 0#datetime.now.hour
    nowMin = 0#datetime.now.minute

    if nowHour<10 and nowMin <10:
        print('출발시간: 0'+str(nowHour)+':0'+str(nowMin))
    elif nowHour>10 and nowMin<10:
        print('출발시간: '+str(nowHour)+':'+str(nowMin))
    else:
        print('출발시간: '+str(nowHour)+':'+str(nowMin))


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
        routeindex = 0
        totalweight = 0
        route = list()
        if len(item) > 2:
            while routeindex <= len(item) - 2:
                weight = G.get_edge_data(item[routeindex],item[routeindex+1])
                totalweight += weight['weight']
                routeindex += 1
        else:
            weight = G.get_edge_data(item[0],item[1])
            totalweight += weight['weight']
        route.append(round(totalweight))
        for trip in item:
            route.append(trip)
        result.append(route)

    
    result = sorted(result,key=lambda triptime: triptime[0])

    modifiedResult = list()

    # 추가 수정사항 - 고속인지 시외인지 구분, 출발, 도착 시간 출력에 포함하기..

    for item in result:
        routeindex = 1 # 가중치순으로 정렬된 루트 리스트에서 첫번째 가중치를 제외한 두번째 인덱스의 값인 터미널이름을 가져오기 위한 변수
        eofdetect = 0 # csv에서 eof를 감지하기 위한 eof 탐지 변수
        addweight = 0 # 추가 가중치 변수

        arrHour = 0 # 도착시간 
        arrMin = 0 # 도착 분

        busType = ''

        route = list()
        timetableList = list()
        # 고속노선과 시외노선 구분하는거 추가 NAI인지 NAEK인지 구분 
        if len(item) > 3:
            while routeindex <= len(item) - 2:
                csvheaderPass = 0
                try:
                    csvindex = 0
                    if os.path.isfile('src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv'):
                        f = open('src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                        f2 = open('src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                        busType = '시외'
                    else:
                        f = open('src/data/exp_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                        f2 = open('src/data/exp_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                        busType = '고속'

                    rdr = csv.reader(f)
                    rdr2 = csv.reader(f2)
                    listcsv = list(rdr)
                    csvindex = len(listcsv) 
                    

                    if csvindex < 2:
                        print('no timetable')
                        print(item[routeindex]+','+item[routeindex+1])
                        addweight += 7000
                        break

                    for line in rdr2:
                        if csvheaderPass < 1:
                            csvheaderPass += 1
                        else:
                            if routeindex < 2:
                                if int(line[3]) > nowHour or (int(line[3]) ==  nowHour and int(line[4]) > nowMin):
                                    arrHour = int(line[7])
                                    arrMin = int(line[8])
                                    routeindex += 1
                                    timetableList.append(line[3])
                                    timetableList.append(line[4])
                                    timetableList.append(line[7])
                                    timetableList.append(line[8])
                                    timetableList.append(busType)
                                    break

                            else:
                                eofdetect += 1
                                if eofdetect > 50:
                                    print('eof detected')
                                    routeindex += 100
                                    addweight += 7000
                                    break
                                if int(line[3]) > arrHour or (int(line[3]) ==  arrHour and int(line[4]) > arrMin):
                                    addweight += (int(line[3]) - arrHour)*60 + int(line[4]) - arrMin
                                    arrHour = int(line[7])
                                    arrMin = int(line[8])
                                    routeindex += 1
                                    timetableList.append(line[3])
                                    timetableList.append(line[4])
                                    timetableList.append(line[7])
                                    timetableList.append(line[8])
                                    timetableList.append(busType)
                                    break

                except:
                    print('no directory... addweight += 7000... 사용불가노선')
                    addweight += 7000
                    routeindex += 1
                    break

            if item[0]+addweight < 7000:
                itemPass = 0
                route.append(item[0]+addweight)
                for val in item:
                    if itemPass == 0:
                        itemPass += 1
                    else:
                        route.append(val)
                route.append(addweight)
                route.append(timetableList)
                modifiedResult.append(route)

        else:
            try:
                csvheaderPass = 0
                addweight = 0
                if os.path.isfile('src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv'):
                    f = open('src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                    f2 = open('src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                    busType = '시외'
                else:
                    f = open('src/data/exp_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                    f2 = open('src/data/exp_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                    busType = '고속'

                rdr = csv.reader(f)
                rdr2 = csv.reader(f2)
                listcsv = list(rdr)
                csvindex = len(listcsv) 
                
                if csvindex < 2:
                    print('no timetable')
                    print(item[routeindex]+','+item[routeindex+1])
                    addweight += 7000

                for line in rdr2:
                    if csvheaderPass < 1:
                        csvheaderPass += 1
                    else:
                        if int(line[3]) > nowHour or (int(line[3]) ==  nowHour and int(line[4]) > nowMin):
                            arrHour = int(line[7])
                            arrMin = int(line[8])
                            timetableList.append(line[3])
                            timetableList.append(line[4])
                            timetableList.append(line[7])
                            timetableList.append(line[8]) 
                            timetableList.append(busType)
                            break
            except:
                print('no directory... addweight += 7000... 사용불가노선')
                addweight += 7000

            if item[0]+addweight < 7000:
                route = [item[0]+addweight,item[1],item[2]]
                route.append(timetableList)
                modifiedResult.append(route) 

    modifiedResult = sorted(modifiedResult,key=lambda triptime: triptime[0])
    for item in modifiedResult:
        print(item)
    