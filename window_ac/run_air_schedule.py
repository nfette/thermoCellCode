import time
from threading import Timer
import itertools
from windowAcState import *

def loadProgram(setfile):
    with open(setfile,'r') as f:
        prog = json.load(f)
    for line in prog:
        line["WacState"] = WacState(**line["WacState"])
        if "time" in line:
            line["time"] = datetime.datetime.strptime(line["time"],whenfmtdata)
    return prog

def runProgramLine(ac):
    for timestamp,setpoint in prog:
        print timestamp, setpoint
        s = adjust(setpoint,ac)
        print s
        ac = mapKeys(ac,s)
        print ac

if __name__ == "__main__":
    print "Usage: run_air_schedule.py schedule.json [-live] [code]"
    ac = loadState()
    serGen = openSerial if "-live" in sys.argv else openFake
    progfile = sys.argv[1]
    prog = loadProgram(progfile)
    now = datetime.datetime.now()
    dprog = dict()
    for line in prog:
        if line["time"] > now:
            dprog[line.pop("time")] = line
    del prog

    with serGen() as ser:
        time.sleep(5)
        
        if len(sys.argv) > 3:
            s = sys.argv[3]
            print ">", s
            ac = echo(s,ac,ser)
            saveState(ac)
            time.sleep(1)
        while (ser.inWaiting()):
            print "Remote:",ser.readline()
                
        while dprog:
            print "\b" * 80,
            now = datetime.datetime.now()
            t_do = [t for t in dprog if t < now]
            for t in t_do:
                line = dprog.pop(t)
                print t
                print "Setpoints:"
                print line["WacState"]
                print line["relayA"]
                print line["relayB"]
                
                s = adjust(line["WacState"], ac)
                s += "a" if line["relayA"] else "A"
                s += "b" if line["relayB"] else "B"
                print ">", s
                ac = echo(s,ac,ser)
                saveState(ac)
                print

                time.sleep(1)
            while (ser.inWaiting()):
                print "Remote:",ser.readline()

            if dprog:
                keys=dprog.keys()
                keys.sort()
                print "time to next: ", keys[0] - now,
                print "time to complete: ", keys[-1] - now,
                time.sleep(0.1)
            else:
                print "Program complete."
