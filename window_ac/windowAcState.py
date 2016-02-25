import serial
import json
import time

defaultFile = 'ac_state.json'

modes = 'Energy Saver,Cool,Fan,Heat'.split(',')
modesMap = dict(list(enumerate(modes)))
modesMapBack = dict([v,k] for k,v in modesMap.items())
class windowAC:
    def __init__(self):
        self.power = False
        self.mode = 2
        self.fan = 1 # 1 or 2
        self.temp = 60
        self.timer = 0
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
            self.power = not self.power
            return True
        elif c == 'm':
            self.mode = (self.mode + 1) % 4
            return True
        elif c == 'f':
            self.fan = self.fan % 2 + 1
            return True
        elif c == 'u':
            self.temp = min(self.temp + 1, 86)
            return True
        elif c == 'd':
            self.temp = max(self.temp - 1, 60)
            return True
        elif c == 't':
            self.timer = (self.timer + 1) % 25
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
        return """"power" : {self.power}
"mode" : {mode}
"fan" : {self.fan}
"temp" : {self.temp}
"timer" : {self.timer}""".format(self=self,mode=modesMap[self.mode])

    def toJSON(self, f=None):
        d = dict(power=self.power,
                               mode=modesMap[self.mode],
                               fan=self.fan,
                               temp=self.temp,
                               timer=self.timer)
        if f:
            json.dump(d, f)
        else:
            return json.dumps()
        
    def fromJSON(self, source):
        if source.read:
            obj = json.load(source)
        else:
            obj = json.loads(source)
        self.power = obj['power']
        self.mode=modesMapBack[obj['mode']]
        self.fan=obj['fan']
        self.temp=obj['temp']
        self.timer=obj['timer']

class linkedAC:
    def __init__(self,ac,ser):
        self.ac = ac
        self.ser = ser
        self.link = True
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
        if c == 'l':
            self.link = not self.link
        elif self.ac.doChar(c):
            if self.link:
                self.ser.write(c)
                time.sleep(1)
        else:
            print "Input ignored"
        
        while (self.ser.inWaiting()):
            print "Remote:",self.ser.readline()
    def __repr__(self):
        return "Link connected : {}".format(self.link)

def openSerial():
    return serial.Serial('COM4',timeout=1)
    
def interact(ac):
    with openSerial() as ser:
        print ser
        lac = linkedAC(ac, ser)
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
        ac.fromJSON(f)
def saveState(ac):
    with open(defaultFile,'w') as f:
        ac.toJSON(f)

if __name__ == "__main__":
    ac = windowAC()
    loadState(ac)

    interact(ac)
