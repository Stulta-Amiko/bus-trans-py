from src import busGraph_debug
from src import busGraph
import sys

#departTerminal, arriveTerminal, departHour, departMin = sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
departTerminal, arriveTerminal, departHour, departMin = '진주','충주',0,0


print(busGraph_debug.trans(departTerminal,arriveTerminal,departHour,departMin))