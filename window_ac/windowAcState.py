import serial
import json
import time

defaultFile = 'ac_state.json'

modes = 'Energy Saver,Cool,Fan,Heat'.split(',')
modesMap = dict(list(enumerate(modes)))
modesMapBack = dict([v,k] for k,v in modesMap.items())
class windowACdata:
    def __init__(self):
        self.power = False
        self.mode = 2
        self.fan = 1 # 1 or 2
        self.temp = 60
        self.timer = 0
    def __eq__(self, other):
        return (self.power == other.power) \
               and (self.mode == other.mode) \
               and (self.fan == other.fan) \
               and (self.temp == other.temp) \
               and (self.timer == other.timer)
    def toDict(self):
        return dict(power=self.power,
                   mode=modesMap[self.mode],
                   fan=self.fan,
                   temp=self.temp,
                   timer=self.timer)        
    def fromDict(self, d):
        self.power = d['power']
        self.mode=modesMapBack[d['mode']]
        self.fan=d['fan']
        self.temp=d['temp']
        self.timer=d['timer']
        
class windowAC(object):
    def __init__(self,data):
        self.data = data
    def togglePower(self):
        self.doChar('p')
    def toggleMode(self):
        self.doChar('m')
    def toggleFan(self):
        self.doChar('f')
    def toggleTempUp(self):
        self.doChar('u')
    def toggleTempDown(self):
        self.doChar('d')
    def toggleTimer(self):
        self.doChar('t')
    def doChar(self,c):
        if c == 'p':
            self.data.power = not self.data.power
            return True
        elif c == 'm':
            if self.data.power:
                self.data.mode = (self.data.mode + 1) % 4
            return True
        elif c == 'f':
            if self.data.power:
                self.data.fan = self.data.fan % 2 + 1
            return True
        elif c == 'u':
            if self.data.power:
                self.data.temp = min(self.data.temp + 1, 86)
            return True
        elif c == 'd':
            if self.data.power:
                self.data.temp = max(self.data.temp - 1, 60)
            return True
        elif c == 't':
            if self.data.power:
                self.data.timer = (self.data.timer + 1) % 25
            return True
        else:
            return False
        """
        fun = {'p': self.togglePower,
               'u': self.toggleTempUp,
               'd': self.toggleTempDown,
               'f': self.toggleFan,
               'm': self.toggleMode,
               't': self.toggleTimer}
        if c in fun:
            fun[c]()
            return True
        else:
            return False
        """

    __doChar = doChar
        
    def __repr__(self):
        return """"power" : {data.power}
"mode" : {mode}
"fan" : {data.fan}
"temp" : {data.temp}
"timer" : {data.timer}""".format(data=self.data,mode=modesMap[self.data.mode])

class linkedAC(windowAC):
    def __init__(self,data,ser):
        super(linkedAC,self).__init__(data)
        self.ser = ser
        self.link = True
    def doChar(self,c):
        if c == 'l':
            self.link = not self.link
        elif super(linkedAC,self).doChar(c):
            if self.link:
                self.ser.write(c)
                time.sleep(1)
        else:
            print "Input ignored"
        
        if self.ser:
            while (self.ser.inWaiting()):
                print "Remote:",self.ser.readline()
    def __repr__(self):
        return "Link connected : {}".format(self.link)

def openSerial():
    return serial.Serial('COM4',timeout=1)
    
def interact(ac,ser=None):
    print ser
    lac = linkedAC(ac.data, ser)
    print lac
    print ac
    while True:
        for c in raw_input("[pudftml]:"):
            print c
            lac.doChar(c)
            print lac
            print ac
            saveState(ac)

def loadState(ac):
    with open(defaultFile,'r') as f:
        ac.data.fromDict(json.load(f))
def saveState(ac):
    with open(defaultFile,'w') as f:
        json.dump(ac.data.toDict(),f)

# Modify lac to match the state of setpoint.
def adjust(setpoint,ac):
    if ac.data != setpoint:
        if not ac.data.power:
            ac.togglePower()

        while ac.data.mode != setpoint.mode:
            ac.toggleMode()
        while ac.data.fan != setpoint.fan:
            ac.toggleFan()
        while ac.data.timer != setpoint.timer:
            ac.toggleTimer()
        while ac.data.temp < setpoint.temp:
            ac.toggleTempUp()
        while ac.data.temp > setpoint.temp:
            ac.toggleTempDown()
        
        if ac.data.power != setpoint.power:
            ac.togglePower()

def runProgram(setfile,ac):
    with open(setfile,'r') as f:
        prog = json.load(f)
    for ts, sp in prog:
        timestamp = ts
        setpoint = windowACdata()
        setpoint.fromDict(sp)
        print timestamp, setpoint

if __name__ == "__main__":
    ac = windowAC(windowACdata())
    loadState(ac)

    interact(ac)
