import sys
import json
import datetime

whenfmtdata = "%Y-%m-%dT%H:%M:%S"

# For a program giving delaySecs, convert to timestamps.
# Modifies the program and outputs nothing.
def applyTemplate(prog,tstart):
    delaySecs = 0
    for line in prog:
        delaySecs += line.pop("delaySecs")
        line["time"] = (tstart + datetime.timedelta(0,delaySecs)).strftime(whenfmtdata)

def saveProgram(prog,outfile):
    with open(outfile,'w') as fout:
        json.dump(prog, fout, indent=4, separators=(',', ': '))

def loadProgram(setfile):
    with open(setfile,'r') as f:
        prog = json.load(f)
    return prog

if __name__ == "__main__":
    print "Usage: applyTemplate.py template output tstart"
    template = sys.argv[1]
    print "Template: ", template
    output = sys.argv[2]
    print "output: ", output
    tstart = sys.argv[3]
    if tstart == "now":
        tstart = datetime.datetime.now()
    else:
        tstart = datetime.datetime.strptime(tstart, whenfmtdata)
    print "tstart: ", tstart
    prog = loadProgram(template)
    print prog
    applyTemplate(prog, tstart)
    saveProgram(prog, output)
