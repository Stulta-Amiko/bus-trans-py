
def printJson(modifiedResult):    
    print('{')
    print('"item": [')
    for idx,item in enumerate(modifiedResult):
        if len(item) == 4:
            print('{')
            print('"totalTime": '+str(item[0])+',')
            print('"departTmn": "'+item[1]+'",')
            print('"arriveTmn": "'+item[2]+'",')
            print('"timetable": [{')
            #for time in item[3]:
            print('"count": 0,')
            print('"departTmnHour": '+str(item[3][0])+',')
            print('"departTmnMin": '+str(item[3][1])+',')
            print('"arriveTmnHour": '+str(item[3][2])+',')
            print('"arriveTmnMin": '+str(item[3][3])+',')
            print('"busType": "'+item[3][4]+'"')
            print('}]')
            if idx == len(modifiedResult) - 1:
                print('}')
            else:
                print('},')
        elif len(item) > 4:
            print('{')
            print('"totalTime": '+str(item[0])+',')
            print('"transferTime": '+str(item[len(item)-2])+',')
            for i in range(1,len(item)-2):
                if i == 1:
                    print('"departTmn": "'+item[1]+'",')
                elif i == len(item)-3:
                    print('"arriveTmn": "'+item[len(item)-3]+'",')
                else:
                    print('"layoverTmn'+str(i-1)+'": "'+item[i]+'",')
            print('"item": [')
            for i in range(0,int((len(item[len(item)-1]))/5)):
                print('{')
                print('"count": '+str(i)+',')
                print('"departTmnHour": '+str(item[len(item)-1][i*5])+',')
                print('"departTmnMin": '+str(item[len(item)-1][i*5+1])+',')
                print('"arriveTmnHour": '+str(item[len(item)-1][i*5+2])+',')
                print('"arriveTmnMin": '+str(item[len(item)-1][i*5+3])+',')
                print('"busType": "'+item[len(item)-1][i*5+4]+'"')
                if i == (len(item[len(item)-1]))/5 - 1:
                    print('}')
                else:
                    print('},')
            print(']')
            if idx == len(modifiedResult) - 1:
                print('}')
            else:
                print('},')
    print(']')
    print('}')
    return ''