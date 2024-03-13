import csv


def find(text):
    departSearch = input(text + "지를 입력해 주세요.\n")

    if(departSearch == 0):
        return 0

    f = open('./data/Express_Bus_Route_Detailed.csv','r')
    rdr = csv.reader(f)
    result = []

    for line in rdr:
        if not(line[2] in result):
            result.append(line[2])

    f = open('./data/Intercity_Bus_Route_Detailed.csv','r')
    rdr = csv.reader(f)

    for line in rdr:
        if not(line[2] in result):
            result.append(line[2])

    search = list(filter(lambda x: departSearch in x,result))

    for idx,val in enumerate(search):
        print(str(idx+1) + val)

    resultIndex = input()

    depart = search[int(resultIndex)-1]

    return depart