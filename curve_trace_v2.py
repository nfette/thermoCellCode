# -*- coding: utf-8
"""
Replacement for measure_open_circuit.py
Created: 2015-09-18 by Nicholas Fette

This module loops in curve
"""

from __future__ import print_function
import libkeithley6517b
import siteDefs
import numpy as np
import datetime
import sys
import json
import itertools
from measure_open_circuit import configureOpenCircuitVoltage,readOpenCircuitVoltage

# Constants
whenfmtfile = "%Y-%m-%dT%H=%M=%S.%f"
whenfmtdata = "%Y-%m-%dT%H:%M:%S.%f"
subfolder = "open_circuit_voltage/"
fields = ("ComputerTime","Voltage","Vsource","Rsensor","Rbypass","OCcount")
deltaV = 0.01
VSenseThreshold = 1e-4
showfmt = "{:>4} {:16} {:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f}"
showfieldfmt=showfmt.replace(".3f","")
showfields = ("i","when","Vsrc","Vcell/mV","I/mA","P/uW","I_sc","Pmax")

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

"Your file should have these fields in a dictionary."
def readConfig(config):
    Rsensor = config["Rsensor"]
    Rbypass = config["Rbypass"]
    VSourceLimit = config["VSourceLimit"]
    return Rsensor, Rbypass, VSourceLimit

def sourceAndRead(inst,Vso):
    when = datetime.datetime.now()
    inst.write(":SOUR:VOLT {}".format(Vso))
    response = map(libkeithley6517b.splitAndSwapNumUnit2,
                   inst.query(":SENS:DATA:FRES?").strip().split(','))
    #units = tuple([b for a,b in response])
    #vals = tuple([a for a,b in response])
    #result = np.array(vals,
    #                  dtype={'names':units,'formats':[np.double]*len(units)})
    result = dict(response)
    Vread = result['VDC']
    Vsrc = result['Vsrc']
    return when,Vsrc,Vread

def loopy(inst,config,outputFile,show=False,showHeads=True):
    Rsensor, Rbypass, VSourceLimit = readConfig(config)
    Vsrc = 0
    # Configure measuring
    inst.write(":SENS:FUNC 'VOLT'")
    # Setup so that each record is like {}VDC,{}secs,{}RDNG#,{}Vsrc
    inst.write(":FORM:ELEM READ,RNUM,UNIT,TST,VSO")
    # Turn off zero check
    inst.write(":SYST:ZCH 0")
    # Start measuring
    inst.write(":TRIG:DEL 0.1")
    inst.write(":INIT:CONT 1")
    #inst.write(":INIT:IMM")
    # Turn on voltage source
    inst.write(":SOUR:VOLT 0")
    inst.write(":OUTP 1")
    # Get sample measurement and read the units
    when, Vsrc, Vread = sourceAndRead(inst,Vsrc)
    E_oc = -Vread
    I_sc = 0
    P_max = 0
    if show and showHeads:
        pass
    try:
        while (abs(Vread) > VSenseThreshold) and (abs(Vsrc) < VSourceLimit):
            Vold = Vread
            when,Vsrc,Vread = sourceAndRead(inst,Vsrc)
            whenstr = when.strftime(whenfmtdata)
            outstr = '{},{},{},{},{},{}\n'.format(
                whenstr, Vread, Vsrc, Rsensor, Rbypass,0)
            outputFile.write(outstr)
            
            Vsens = Vsrc - Vread
            Vcell = -Vread
            I = Vsens / Rsensor + Vcell/Rbypass
            P = Vcell * I
            P_max = max(P,P_max)
            I_sc = max(I_sc,abs(I))
            print('\b'*80,end="")
            print(showfmt.format(
                0, when.strftime("%H:%M:%S.%f"),
                Vsrc, 1e3*Vcell, 1e3*I, 1e6*P,
                1e3*I_sc,1e6*P_max),end="")
            # To continue or not to continue
            if np.sign(Vread) != np.sign(Vold):
                break
            else:
                Vsrc -= deltaV * np.sign(Vread)
    finally:
        inst.write(":OUTP 0")
        inst.write(":SYST:ZCH 1")
    if show and showHeads:
        print()
    return when,E_oc,I_sc,P_max

def main(config, f, headers=True,nsweeps=None,device=None):
    print("""Please verify the following. According to config file,
Sensing resistor R = {} ohms
 Bypass resistor R = {} ohms""".format(config["Rsensor"],
                                       config["Rbypass"]))

    if headers:
        f.write(",".join(fields)+"\n")
        
    if nsweeps:
        counter = range(nsweeps)
    else:
        counter = itertools.count(0)

    if device:
        rm,inst = device
    else:
        rm,inst = libkeithley6517b.getDevice()
        print("*IDN? > {}".format(inst.query("*IDN?")))
    
    inst.write("*RST; *CLS;")
    libkeithley6517b.syncClock(inst)

    print(showfieldfmt.format(*showfields))
    print("",end="")

    E_oc,I_sc,P_max = 0,0,0
    try:
        for i in counter:
            Vsrc,Rsensor = 0,1e300
            Rbypass = config["Rbypass"]
            configureOpenCircuitVoltage(inst)
            for j in range(1,1+config["Waits"]):
                when,Vread,unit=readOpenCircuitVoltage(inst)
                whenstr = when.strftime(whenfmtdata)
                outstr = '{},{},{},{},{},{}\n'.format(
                    whenstr, Vread, Vsrc, Rsensor, Rbypass,j)
                f.write(outstr)
                Vsens = Vsrc - Vread
                Vcell = -Vread
                I = Vsens / Rsensor + Vcell/Rbypass
                P = Vcell * I
                print('\b'*80,end="")
                print(showfmt.format(
                    j, when.strftime("%H:%M:%S.%f"),
                    Vsrc, 1e3*Vcell, 1e3*I, 1e6*P,
                    1e3*I_sc,1e6*P_max),end="")
            # Curve trace
            when,E_oc,I_sc,P_max=loopy(inst,config,f,True,False)
            f.flush()
    except KeyboardInterrupt:
        pass
    finally:
        print()
        print(inst.write(":SYST:ZCH 1"))
        print(inst.query(":SYST:ZCH?"))
        inst.close()

if __name__ == "__main__":
    print("Usage: curve_trace_v2.py configFile.json [outputfile.dat]")
    configFilename = sys.argv[1]
    print("Loading config from {}".format(configFilename))
    with open(configFilename,'r') as fconfig:
        config = json.load(fconfig)
    try:
        outputFilename = sys.argv[2]
        headers = False
    except:
        when = datetime.datetime.now()
        outputFilename = getFilename(when)
        headers = True
    print("Saving to {}".format(outputFilename))
    with open(outputFilename,'a') as f2:
        main(config, f2, headers)

    
