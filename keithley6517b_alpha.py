from __future__ import print_function
import visa
import re
import numpy as np

def getDevice():
    rm = visa.ResourceManager()
    result = rm.list_resources()
    #print(result)
    for name in result:
        if name.find("GPIB") >= 0:
            myGPIBname = name
            break
    inst = rm.open_resource(myGPIBname)
    #print(inst.query("*IDN?"))
    return inst

useful_string1 = """*rst;*CLS;
stat:meas:enab 512;
*sre 1;

:SENS:FUNC 'VOLT';
:SENS:CURR:RANG:AUTO ON;

:TSEQ:TYPE STSW;
:TSEQ:STSW:STAR {};
:TSEQ:STSW:STOP {};
:TSEQ:STSW:STEP {};
:TSEQ:STSW:STIM {};
:TSEQ:TSO imm;


"""

useful_string2 = "*OPC?"
useful_string3 = ":TSEQ:ARM"
useful_string4 = ":TRACE:DATA?"

def runUpStairs(start, stop, step, stim):
    inst.write(useful_string1.format(start, stop, step, stim))
    print(inst.query(useful_string2))
    
    inst.write(useful_string3)
    inst.wait_for_srq()
    response = inst.query(useful_string4)
    p = re.compile(r'(.+?)(\D+)$')
    theArray = []
    for b in response.split(','):
        m = p.match(b)
        val,unit = m.groups()
        theArray.append(float(val))
    result = np.array(theArray).reshape((101,3))
    return theArray

if __name__ == "__main__":
    inst = getDevice()
    print(inst.query("*IDN?"))
    start, stop, step, stim = 0.0, 1.0, 0.01, 0.0
    result = runUpStairs(start, stop, step, stim)
    
    
