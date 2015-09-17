# -*- coding: utf-8
"""
This will the IV curve tracer cum open cicruit mode.
To learn how to do, look for Reference manual '6517b-901-01--B-Jun 2009--Ref.pdf'.
Chapter 14 contains SCPI command reference.

Documentation for PyVISA is online.
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
import time
import unpickletest2
import libkeithley6517b
import tabulate

# These have to follow the order in the manual
useful_string0 = ":FORM:ELEM READ,RNUM,UNIT,TST,STAT,VSO"
# Example output looks like this:
example_read = "+01.01103E+00NVDC,09:00:20.00,26-Mar-2015,+01945RDNG#,+0001.000Vsrc"
# However, when running a sequence mode, the VSO is ommitted, like:
example_read_seq = "+00.00849E+00NVDC,09:43:20.00,26-Mar-2015,+00000RDNG#"

# Do not need to :SYST:TST:REL:RES
useful_string1 = """*rst;*CLS;
stat:meas:enab 512;
*sre 1;

:SYST:TST:TYPE REL;
:TRAC:TST:FORM ABS;

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



def runUpStairs(inst, start, stop, step, stim, shape):
    global response
    inst.write(useful_string1.format(start, stop, step, stim))
    print(inst.query(useful_string2))

    # Some options ...
    #inst.write(":SYST:TST:TYPE RTCL") # options: REL or RTCL.
    #inst.write(":FORM:ELEM READ,RNUM,UNIT,TST,STAT")

    # options: ABS or DELT.
    # Interesting fact: if :SYST:TST:TYPE? is RTCL and :TRACE:TST:FORM? is ABS,
    #     then you get a RTCL value (hour:min:sec.00,day-month-year).
    # If :SYST:TST:TYPE? is RTCL and :TRACE:TST:FORM? is DELT,
    #     then you get a RTCL value (hour:min:sec.00,day-month-year).
    # If :SYST:TST:TYPE? is REL and :TRACE:TST:FORM? is ABS,
    #     then you get a value with unit "secs".
    # If :SYST:TST:TYPE? is REL and :TRACE:TST:FORM? is DELT,
    #     then you get an "DELTA"+value+"SECS".
    inst.write(":SYST:TST:TYPE REL")
    inst.write(":TRAC:TST:FORM ABS")
    
    # From manual: READ,RNUM,UNIT,STAT are always enabled.
    # Try it: if you request them, you get synatx error.
    # However, they do show up in :TRACE:ELEM?
    # Allowed options to request: TST,HUM,CHAN,ETEM,VSO or NONE
    inst.write(":TRACE:ELEM TST,VSO")

    # Found a bug in Kiethley. If you do :SYST:TST:TYPE RTCL, then
    # :TRAC:DATA? will be formatted in RTCL timestamp, although the
    # :TRACE:TST:FORM? still returns eg. ABS. A nasty trick!
    
    inst.write(useful_string3)
    inst.wait_for_srq()
    response = inst.query(useful_string4)
    #print(response)
    p = re.compile(r'(.+?)(\D*)$')
    theArray = []
    unitArray = []
    for b in response.split(','):
        #print(b)
        m = p.match(b)
        val,unit = m.groups()
        #if val.contains(':'):
        #    theArray.append(datetime.fromstring(val)
        try:
            theArray.append(float(val))
        except:
            theArray.append(-999)
            #print("Could not parse your number, '{}'".format(val))
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

def main(date, outputPickle, outputPlot, device=None):
    if device:
        rm,inst = device
    else:
        rm,inst = libkeithley6517b.getDevice()
        print(inst.query("*IDN?"))
    inst.write(':DISP:TEXT:DATA "Start curve trace"')
    inst.write(':DISP:TEXT:STAT 1')
    time.sleep(0.1)
    inst.write(':DISP:TEXT:STAT 0')
    inst.write(':DISP:WIND2:TEXT:STAT 0')
    
    inst.write(useful_string0)
    start, stop, step, stim = -0.05, 0.2, 0.005, 0.01
    npoints = 1+(stop-start)/step
    nfields = 3
    shape = npoints,nfields
    #inst.write(":SYST:TST:TYPE RTCL")

    print("Stair sweep")
    print(tabulate.tabulate(
        [[start, stop, step, stim]],["start","stop","step","stim"]))
    result, units = runUpStairs(inst, start, stop, step, stim, shape)
    # If copper electolyte...
    #R_current_sensor = 98.3 # ohms
    # If Cu+EDTA electrolyte...
    R_current_sensor = 972.0 # ohms
    calibration = libkeithley6517b.pvpanelType(start, stop, step, stim, nfields,
                                  units, result, R_current_sensor,
                                  date)
    with open(outputPickle, 'wb') as f:
        pickle.dump(calibration,f)

    print(tabulate.tabulate(result,headers=map(str,units[0])))    
    
    inst.write(':DISP:TEXT:DATA "Done curve trace"')
    inst.write(':DISP:TEXT:DATA "Hi, Jon!"')
    inst.write(':DISP:TEXT:STAT 1')
    time.sleep(0.1)
    inst.write(':DISP:TEXT:STAT 0')
    inst.write(':DISP:WIND2:TEXT:STAT 0')
    
def picklePlotFileNames(date):
    datestr = date.isoformat().replace(':','=')
    basename = siteDefs.data_base_dir + "curve_traces/"
    outputPickle = "{}{}.pkl".format(basename, datestr)
    outputPlot = "{}{}.png".format(basename, datestr)
    return outputPickle, outputPlot

def main2(device=None):
    date = datetime.datetime.now()
    outputPickle, outputPlot = picklePlotFileNames(date)
    main(date, outputPickle, outputPlot, device)
    print("Saved: \n{}\n{}".format(outputPickle, outputPlot))
    unpickletest2.main(outputPickle,True)
    
if __name__ == "__main__":
    main2()
