import serial
import json
import time
import datetime
from collections import namedtuple
import sys

defaultFile = 'ac_state.json'
whenfmtdata = "%Y-%m-%dT%H:%M:%S"

modes = 'Energy Saver,Cool,Fan,Heat'.split(',')
def nextMode(ms):
    mi = modes.index(ms)
    mi = (mi + 1) % 4
    return modes[mi]
    
WacState=namedtuple("WacState","power,mode,fan,temp,timer")
def isValid(self):
    return (type(self.power) == bool \
            and self.mode in modes \
            and self.fan in (1,2) \
            and self.temp in range(60,86+1) \
            and self.timer in range(0,24+1))
WacState.isValid = isValid

def loadState():
    with open(defaultFile,'r') as f:
        return WacState(**json.load(f))
def saveState(state):
    with open(defaultFile,'w') as f:
        json.dump(state._asdict(), f, indent=4, separators=(',', ': '))

def togglePower(state):
    return state._replace(power=not state.power)
def toggleMode(state):
    if state.power:
        return state._replace(mode=nextMode(state.mode))
    else:
        return state
def toggleFan(state):
    if state.power:
        return state._replace(fan=state.fan % 2 + 1)
    else:
        return state
def toggleTempUp(state):
    if state.power:
        return state._replace(temp=min(state.temp + 1, 86))
    else:
        return state
def toggleTempDown(state):
    if state.power:
        return state._replace(temp=max(state.temp - 1, 60))
    else:
        return state
def toggleTimer(state):
    if state.power:
        return state._replace(timer=(state.timer + 1) % 25)
    else:
        return state
    
keyMap = {'p': togglePower,
           'u': toggleTempUp,
           'd': toggleTempDown,
           'f': toggleFan,
           'm': toggleMode,
           't': toggleTimer}

def mapKeys(state,keys):
    for key in keys:
        if key in keyMap: # otherwise ignore the key
            state = keyMap[key](state)
    return state

# Attempt to match the state of setpoint.
# Outputs the sequence required to do it, or false if unreachable.
def adjust(setpoint,ac):
    if not (setpoint.isValid() and ac.isValid()):
        return False
    s = ''
    if ac != setpoint:
        if not ac.power:
            ac = togglePower(ac)
            s += 'p'
        while ac.mode != setpoint.mode:
            ac = toggleMode(ac)
            s += 'm'
        while ac.fan != setpoint.fan:
            ac = toggleFan(ac)
            s += 'f'
        while ac.timer != setpoint.timer:
            ac = toggleTimer(ac)
            s += 't'
        while ac.temp < setpoint.temp:
            ac = toggleTempUp(ac)
            s += 'u'
        while ac.temp > setpoint.temp:
            ac = toggleTempDown(ac)
            s += 'd'
        
        if ac.power != setpoint.power:
            togglePower(ac)
            s += 'p'
    return s

def openSerial():
    return serial.Serial('COM4',timeout=1)

# Tee and feed the control string cs into both
#   ac - state
#   ser - serial object
# Returns the updated state
def echo(cs,ac,ser):
    ser.write(cs)
    return mapKeys(ac,cs)

class fakeSerial:
    def write(self,c):
        pass
    def inWaiting(self):
        return 0
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        pass

def openFake():
    return fakeSerial()

if __name__ == "__main__":
    if "-help" in sys.argv:
        print "Usage: windowAcState.py [-live] [-quiet]"
    ac = loadState()
    serGen = openSerial if "-live" in sys.argv else openFake
    prompt = "" if "-quiet" in sys.argv else "[pmftudaAbBq]> "
    with serGen() as ser:
        while (ser.inWaiting()):
            print "Remote:",ser.readline()
        while True:
            try:
                s = raw_input(prompt)
                if s == 'q':
                    break
                ac = echo(s,ac,ser)
                print ac
                saveState(ac)
                while (ser.inWaiting()):
                    print "Remote:",ser.readline()
            except EOFError as e:
                break
