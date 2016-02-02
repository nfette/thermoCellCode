import serial

modes = 'Energy Saver,Cool,Fan,Heat'.split(',')
modesMap = dict(list(enumerate(modes)))
class windowAC:
    def __init__(self,ser):
        self.ser = ser
        self.power = False
        self.mode = 0
        self.fan = 0
        self.temp = 60
        self.timer = 0
    def togglePower(self):
        ser.write('p')
        self.power = not self.power
    def toggleMode(self):
        ser.write('m')
        self.mode = (self.mode + 1) % 4
    def toggleFan(self):
        ser.write('f')
        self.fan = (self.fan + 1) % 2
    def toggleTempUp(self):
        ser.write('u')
        self.temp = min(self.temp + 1, 86)
    def toggleTempDown(self):
        ser.write('d')
        self.temp = max(self.temp - 1, 60)
    def toggleTimer(self):
        ser.write('t')
        self.timer = (self.timer + 1) % 25
    def doChar(self,c):
        if c == 'p':
            self.togglePower()
        elif c == 'u':
            self.toggleTempUp()
        elif c == 'd':
            self.toggleTempDown()
        elif c == 'f':
            self.toggleFan()
        elif c == 'm':
            self.toggleMode()
        elif c == 't':
            self.toggleTimer()
        while (ser.inWaiting()):
            print "Remote:",ser.readline()
    def __repr__(self):
        return """power = {self.power}
mode = {mode}
fan = {self.fan}
temp = {self.temp}
timer = {self.timer}""".format(self=self,mode=modesMap[self.mode])

    
if __name__ == "__main__":
    with serial.Serial('COM4',timeout=1) as ser:
        ac = windowAC(ser)
        print ac
        while True:
            for c in raw_input("[pudftm]:"):
                print c
                ac.doChar(c)
                print ac
        
