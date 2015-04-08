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
# However, when running a sequence mode, the VSO is ommitted, like:
example_read_seq = "+00.00849E+00NVDC,09:43:20.00,26-Mar-2015,+00000RDNG#"

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
    inst.write(":TRACE:TST:FORM ABS")
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
    print(response)
    p = re.compile(r'(.+?)(\D*)$')
    theArray = []
    unitArray = []
    for b in response.split(','):
        print(b)
        m = p.match(b)
        val,unit = m.groups()
        #if val.contains(':'):
        #    theArray.append(datetime.fromstring(val)
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
    inst.write(':DISP:TEXT:DATA "Clinton 2016"')
    inst.write(':DISP:TEXT:STAT 1')
    inst.write(':DISP:WIND2:TEXT:DATA "Loading   ..."')
    inst.write(':DISP:WIND2:TEXT:STAT 1')
    time.sleep(1)
    inst.write(':DISP:WIND2:TEXT:DATA "Loading   ... platform"')
    time.sleep(1)
    inst.write(':DISP:WIND2:TEXT:DATA "Loading   ... electrons"')
    time.sleep(1)
    inst.write(':DISP:WIND2:TEXT:DATA "electrons ... electrons"')
    time.sleep(1)
    inst.write(':DISP:TEXT:STAT 0')
    inst.write(':DISP:WIND2:TEXT:STAT 0')
    
    inst.write(useful_string0)
    start, stop, step, stim = -0.0, 0.5, 0.01, 0.0
    npoints = 1+(stop-start)/step
    nfields = 3
    shape = npoints,nfields
    inst.write(":SYST:TST:TYPE RTCL")
    for n in range(10):
        sourceVoltageReadVoltage(inst,1.0)
    result, units = runUpStairs(inst, start, stop, step, stim, shape)
    #Vin = np.arange(start,stop,step)
    Vin = np.linspace(start,stop,npoints)
    #print(result)
    Vout, timestamp, iSample = result.T
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

    
