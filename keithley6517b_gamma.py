# -*- coding: utf-8
"""
This is the IV curve tracer. Run every time you want curve trace info.
"""

from __future__ import print_function
import visa
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple
import pickle
import datetime
import siteDefs

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
    return rm,inst

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

fields = ['start','stop','step','stim','nfields','units','data',
          'r_current_sensor','date']
pvpanelType = namedtuple('pvpanelType',fields)

def runUpStairs(inst, start, stop, step, stim, shape):
    inst.write(useful_string1.format(start, stop, step, stim))
    print(inst.query(useful_string2))
    
    inst.write(useful_string3)
    inst.wait_for_srq()
    response = inst.query(useful_string4)
    p = re.compile(r'(.+?)(\D+)$')
    theArray = []
    unitArray = []
    for b in response.split(','):
        m = p.match(b)
        val,unit = m.groups()
        theArray.append(float(val))
        unitArray.append(unit)
    result = np.array(theArray).reshape(shape)
    units = np.array(unitArray).reshape(shape)
    return result, units

def main(date, outputPickle, outputPlot):
    rm,inst = getDevice()
    print(inst.query("*IDN?"))
    start, stop, step, stim = 0.0, 0.5, 0.01, 0.0
    npoints = 1+(stop-start)/step
    nfields = 3
    shape = npoints,nfields
    result, units = runUpStairs(inst, start, stop, step, stim, shape)
    #Vin = np.arange(start,stop,step)
    Vin = np.linspace(start,stop,npoints)
    #print(result)
    Vout, time, iSample = result.T
    R_current_sensor = 98.3 # ohms
    V_current_sensor = Vin - Vout
    I = V_current_sensor / R_current_sensor
    calibration = pvpanelType(start, stop, step, stim, nfields,
                                  units, result, R_current_sensor,
                                  date)
    with open(outputPickle, 'wb') as f:
        pickle.dump(calibration,f)

    plt.cla()
    plt.plot(I, Vout,'o')
    plt.xlabel('DUT current ($I/$[amps])')
    plt.ylabel('DUT voltage ($V/$[volts])')
    plt.savefig(outputPlot)

if __name__ == "__main__":
    # ohms
    date = datetime.datetime.now()
    datestr = date.isoformat().replace(':','=')
    basename = siteDefs.data_base_dir + "curve_traces/"
    outputPickle = "{}{}.pkl".format(basename, datestr)
    outputPlot = "{}{}.png".format(basename, datestr)
    main(date, outputPickle, outputPlot)
    print("Saved: \n{}\n{}".format(outputPickle, outputPlot))

    
