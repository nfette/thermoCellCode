# -*- coding: utf-8
"""
This module is used as a stand-alone program to collect open-circuit
voltage measurements over time from the thermocell. These data are
appended into a text file for synchronous post-processing (visualization)
using another module.

Note that despite reference manual page 2-28 and 14-37, which indicate that
":SYST:TST:TYPE RTClock" will always give you 24 hour time format,
the menu system has an option for displaying the clock in 12 hour time format.
You must manually navigate the menus to set this correctly to the 24 hour
time format in order to get the correct times after noon. In summary,
the time stamp is worthless unless you know you have done this.

"""
from __future__ import print_function
import libkeithley6517b
import datetime
import siteDefs
import numpy as np
import os.path

# Constants
whenfmtfile = "%Y-%m-%dT%H=%M=%S.%f"
whenfmtdata = "%Y-%m-%dT%H:%M:%S.%f"
subfolder = "open_circuit_voltage/"

# Measure, write to file, loop
def main(f):
    rm,inst = libkeithley6517b.getDevice()
    print(inst.query("*IDN?"))
    print(inst.write("*RST; *CLS;"))
    syncClock(inst)
    configureOpenCircuitVoltage(inst)
    try:
        while True:
            try:
                when,val,unit=readOpenCircuitVoltage(inst)
                print(val,unit)
                whenstr = when.strftime(whenfmtdata)
                f.write("{},{},{}\n".format(whenstr,val,unit))
            except KeyboardInterrupt:
                break
    finally:
        print(inst.write(":SYST:ZCH 1"))
        print(inst.write(":SYST:ZCH?"))
        inst.close()

# Where to open the file
def getFilename(when):
    whenstr = when.strftime(whenfmtfile).replace(":","=")
    fmt = "{}{}{}.dat"
    return fmt.format(siteDefs.data_base_dir,subfolder,whenstr)

# When did you open this file?
def getWhenFromFilename(fname):
    whenstr = os.path.splitext(os.path.basename(fname))[0]
    when = datetime.datetime.strptime(whenstr,whenfmtfile)
    return when

# synchronize the clock
def syncClock(inst):
    # Synchronize the clocks.
    inst.write(":SYST:DATE {}; :SYST:TIME {};".format(
        *datetime.datetime.now().strftime("%Y,%m,%d;%H,%M,%S").split(";")))

def configureOpenCircuitVoltage(inst):
    inst.write(":STAT:MEAS:PRES")
    inst.write(":SYST:ZCH 1")
    inst.write(":CONF:VOLT:DC")
    inst.write(":FORM:ELEM READ,UNIT")
    #inst.write(":FORM:ELEM READ,UNIT,TST"))
    #inst.write(":SYST:TST:TYPE RTClock"))
    inst.write(":SYST:ZCH 0")
    
def readOpenCircuitVoltage(inst):
    when = datetime.datetime.now()
    response = inst.query(":READ?")
    tags = response.strip().split(',')
    val,unit = libkeithley6517b.splitNumUnit(tags[0])
    val = float(val)
    return when,val,unit

if __name__ == "__main__":
    when = datetime.datetime.now()
    filename = getFilename(when)
    print(filename)
    with open(filename,'w') as f:
        main(f)
