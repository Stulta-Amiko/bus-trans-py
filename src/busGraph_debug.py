import networkx as nx
import csv
import os
from src.util import printJson,graph

def trans(depTmn,arrTmn,depHour,depMin):
    G = graph.makeGraph()

    def peek(iterable):
        try:
            first = next(iterable)
        except StopIteration:
            return 0
        return 1

    depart = depTmn
    arrive = arrTmn

    cutoff = 0

    nowHour = depHour
    nowMin = depMin

    simplePath = nx.all_simple_paths(G,depart,arrive,cutoff=cutoff)
    while not peek(simplePath):
        if not peek(simplePath):
            cutoff += 1
            simplePath = nx.all_simple_paths(G,depart,arrive,cutoff=cutoff)

    if cutoff < 2:
        cutoff += 1
        
    simplePath = nx.all_simple_paths(G,depart,arrive,cutoff=cutoff) # 전체경로 찾기 cutoff 중에서 

    result = list()

    for item in simplePath: # networkx 이용해서 총 가중치 구하는 코드
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
        addweight = 0 # 추가 가중치 변수

        arrHour = 0 # 도착시간 
        arrMin = 0 # 도착 분

        busType = ''

        route = list()
        timetableList = list()
        eofdetect = 0 # csv에서 eof를 감지하기 위한 eof 탐지 변수
        # 고속노선과 시외노선 구분하는거 추가 NAI인지 NAEK인지 구분 
        if len(item) > 3:
            while routeindex <= len(item) - 2:
                csvheaderPass = 0
                
                try:
                    csvindex = 0
                    if os.path.isfile('/Users/user/Desktop/mern/pyparse/busroute/src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv'):
                        f = open('/Users/user/Desktop/mern/pyparse/busroute/src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                        busType = '시외'
                    else:
                        f = open('/Users/user/Desktop/mern/pyparse/busroute/src/data/exp_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                        busType = '고속'

                    rdr = csv.reader(f) # csv 파일의 eof 를 판단하기 위한 reader
                    listcsv = list(rdr)
                    csvindex = len(listcsv) 
                    
                    if csvindex < 2:
                        #print('no timetable') # 헤더만 있는경우 추가가중치를 고의적으로 많이줘서 탈락시키기
                        #print(item[routeindex]+','+item[routeindex+1])
                        addweight += 7000
                        break

                    for idx,line in enumerate(listcsv):
                        if csvheaderPass < 1:
                            csvheaderPass += 1 # csv 헤더 패스 
                        else:
                            if routeindex < 2: # 첫 출발일 경우
                                if idx == csvindex - 1:
                                    routeindex += 100
                                    addweight += 7000
                                    break
                                if int(line[3]) > nowHour or (int(line[3]) ==  nowHour and int(line[4]) > nowMin):
                                    arrHour = int(line[7])
                                    arrMin = int(line[8])
                                    routeindex += 1
                                    timetableList.append(line[3]) # 출발 시간
                                    timetableList.append(line[4]) # 출발 분
                                    timetableList.append(line[7]) # 도착 시간
                                    timetableList.append(line[8]) # 도착 분
                                    timetableList.append(busType) # 버스 타입(시외, 고속)
                                    break

                            else: # 그 외 두번째 이후의 출발일 경우 
                                if idx == csvindex - 1:
                                    routeindex += 100
                                    addweight += 7000
                                    break

                                if int(line[3]) > arrHour or (int(line[3]) ==  arrHour and int(line[4]) > arrMin):
                                    addweight += (int(line[3]) - arrHour)*60 + int(line[4]) - arrMin # 추가 가중치 계산
                                    if (int(line[3]) - arrHour)*60 + int(line[4]) - arrMin < 10:
                                        continue
                                    arrHour = int(line[7]) # 환승대기 가중치 계산을 위한 도착 시간 저장
                                    arrMin = int(line[8]) 
                                    routeindex += 1 # 다음 여정으로 넘기기 
                                    timetableList.append(line[3]) # 출발 시간
                                    timetableList.append(line[4]) # 출발 분
                                    timetableList.append(line[7]) # 도착 시간
                                    timetableList.append(line[8]) # 도착 분
                                    timetableList.append(busType) # 버스 타입(시외, 고속)
                                    break

                except:
                    #print('no directory... addweight += 7000... 사용불가노선') # 폴더를 찾지 못하는 경우
                    addweight += 7000 # 노선에서 제외
                    routeindex += 1
                    break

            if item[0]+addweight < 7000: # 전체 가중치가 7000 보다 작은경우
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

        else: # 노선이 직통으로 있는 경우
            try:
                csvheaderPass = 0
                addweight = 0
                if os.path.isfile('/Users/user/Desktop/mern/pyparse/busroute/src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv'):
                    f = open('/Users/user/Desktop/mern/pyparse/busroute/src/data/int_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                    busType = '시외'
                else:
                    f = open('/Users/user/Desktop/mern/pyparse/busroute/src/data/exp_each/'+item[routeindex]+'/'+item[routeindex+1]+'_TimeTable.csv','r+')
                    busType = '고속'

                rdr = csv.reader(f) # csv 파일의 eof 를 판단하기 위한 reader
                listcsv = list(rdr)
                csvindex = len(listcsv) 
                
                if csvindex < 2:
                    #print('no timetable') # 헤더만 있는경우 추가가중치를 고의적으로 많이줘서 탈락시키기
                    #print(item[routeindex]+','+item[routeindex+1])
                    addweight += 7000

                for idx,line in enumerate(listcsv):
                    if csvheaderPass < 1:
                        csvheaderPass += 1
                    else:
                        if idx == csvindex - 1:
                            routeindex += 100
                            addweight += 7000
                            break
                        if int(line[3]) > nowHour or (int(line[3]) ==  nowHour and int(line[4]) > nowMin):
                            timetableList.append(line[3]) # 출발 시간
                            timetableList.append(line[4]) # 출발 분
                            timetableList.append(line[7]) # 도착 시간
                            timetableList.append(line[8]) # 도착 분
                            timetableList.append(busType) # 버스 타입(시외, 고속)
                            break
            except:
                #print('no directory... addweight += 7000... 사용불가노선')
                addweight += 7000

            if item[0]+addweight < 7000:
                route = [item[0]+addweight,item[1],item[2]]
                route.append(timetableList)
                modifiedResult.append(route) 

    modifiedResult = sorted(modifiedResult,key=lambda triptime: triptime[0])
    printJson.printJson(modifiedResult)
    return ''