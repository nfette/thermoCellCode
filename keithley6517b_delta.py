# -*- coding: utf-8
"""
This will the IV curve tracer cum open cicruit mode.
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

# These have to follow the order in the manual
useful_string0 = ":FORM:ELEM READ,RNUM,UNIT,TST,STAT,VSO"
# Example output looks like this:
example_read = "+01.01103E+00NVDC,09:00:20.00,26-Mar-2015,+01945RDNG#,+0001.000Vsrc"

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

useful_string5 = ":SOUR:VOLT {}"
useful_string6 = ":OUTP {:b}"
useful_string7 = ":READ?"

fields = ['start','stop','step','stim','nfields','units','data',
          'r_current_sensor','date']
pvpanelType = namedtuple('pvpanelType',fields)

def runUpStairs(inst, start, stop, step, stim, shape):
    inst.write(useful_string1.format(start, stop, step, stim))
    print(inst.query(useful_string2))
    
    inst.write(useful_string3)
    inst.wait_for_srq()
    response = inst.query(useful_string4)
    print(response)
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

def sourceVoltageReadVoltage(inst,Vin):
    inst.write(useful_string5.format(Vin))
    try:
        inst.write(useful_string6.format(True))
        response = inst.query(useful_string7)
        print(response)
    finally:
        # Make sure we don't leave it running, maybe
        inst.write(useful_string6.format(False))

def main(date, outputPickle, outputPlot):
    rm,inst = getDevice()
    print(inst.query("*IDN?"))
    inst.write(useful_string0)
    start, stop, step, stim = -0.5, 0.5, 0.01, 0.0
    npoints = 1+(stop-start)/step
    nfields = 3
    shape = npoints,nfields
    for n in range(10):
        sourceVoltageReadVoltage(inst,1.0)
    result, units = runUpStairs(inst, start, stop, step, stim, shape)
    #Vin = np.arange(start,stop,step)
    Vin = np.linspace(start,stop,npoints)
    #print(result)
    Vout, time, iSample = result.T
    R_current_sensor = 98.3 # ohms
    V_current_sensor = Vin + Vout
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

    
