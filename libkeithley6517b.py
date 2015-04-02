# -*- coding: utf-8
"""
This module contains library functions for useful commands on the Keithley
and data parsing.

To learn how to do, stufflook for Reference manual:
'6517b-901-01--B-Jun 2009--Ref.pdf'.
Chapter 14 contains SCPI command reference.

Documentation for PyVISA is online.
"""
from __future__ import print_function
import visa
from collections import namedtuple
import re
import datetime
import pickle

"""
    Opening and configuring the device.
"""
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

def configVSO(inst):
    inst.write("""*rst;*CLS;
stat:meas:enab 512;
:SENS:FUNC 'VOLT';
:SENS:CURR:RANG:AUTO ON;
""")
    inst.write(defaultFormat.getFormatCommand())
    
def sourceVoltageReadVoltage(inst,Vin,stayOn=False):
    inst.write(":SOUR:VOLT {}".format(Vin))
    try:
        inst.write(":OUTP {:b}".format(True))
        response = inst.query(":READ?")
        inst.write("OUTP {:b}".format(stayOn))
        return parseRead(defaultFormat, response)
    finally:
        # There was an error. Turn off the voltage source.
        inst.write("OUTP {:b}".format(False))

def configStairSweep(inst):
    inst.write("""*rst;*CLS;
stat:meas:enab 512;
*sre 1;
:SENS:FUNC 'VOLT';
:SENS:CURR:RANG:AUTO ON;
""")
    inst.write(seqFormat.getFormatCommand())

def runUpStairs(inst, start, stop, step, stim):
    inst.write(""":TSEQ:TYPE STSW;
:TSEQ:STSW:STAR {};
:TSEQ:STSW:STOP {};
:TSEQ:STSW:STEP {};
:TSEQ:STSW:STIM {};
:TSEQ:TSO imm;
""".format(start, stop, step, stim))
    print(inst.query("*OPC?"))
    
    inst.write(":TSEQ:ARM")
    inst.wait_for_srq()
    response = inst.query("TRACE:DATA?")
    return parseTraceData(seqFormat, response)

"""
    Read and parse data!
"""

formatFlags = namedtuple('FormatFlags',
                         ['READ','CHAN','RNUM','UNIT','TST',
                          'STAT','HUM','ETEM','VSO'])
formatFlags.commandHead = ":FORM:ELEM"
def getFormatCommand(self):
    return self.commandHead + " " \
           + ",".join([self._fields[i] for i in range(len(self)) if self[i]])
formatFlags.getFormatCommand = getFormatCommand
defaultFormat=formatFlags(True,False,True,True,True,True,False,False,True)
seqFormat = formatFlags(True,False,True,True,True,True,False,False,False)

numUnitPattern = re.compile(r'(.+?)(\D*)$')
def splitNumUnit(s):
    return numUnitPattern.match(s).groups()

readStruct = namedtuple('ReadStruct',
                        ['reading','status','readunit',
                         'timestamp',
                         'rnum',
                         'vso','vsounit'])

def parseRead(format_flags, s, recurse=False):
    """Read a string from the Keithley and output the data."""
    if format_flags.VSO:
        #aread,atime,adate,arnum,avso = s.split(',')
        headache = s.split(',')
        aread,atime,adate,arnum,avso = headache[0:5]
        tail = ','.join(headache[5:])
        #print aread, atime, adate, arnum, avso
        read,readunit = splitNumUnit(aread)
        read = float(read)
        readstatus,readunit = readunit[0],readunit[1:]
        #print read, readstatus, readunit
        tstformat = "%H:%M:%S.%f,%d-%b-%Y"
        tst = datetime.datetime.strptime(atime + "," + adate, tstformat)
        #print tst
        rnum,rnumunit = splitNumUnit(arnum)
        rnum = int(rnum)
        #print rnum, rnumunit
        vso,vsounit = splitNumUnit(avso)
        vso = float(vso)
        #print vso, vsounit
    else:
        headache = s.split(',')
        aread,atime,adate,arnum = headache[0:4]
        tail = ','.join(headache[4:])
        #print aread, atime, adate, arnum, avso
        read,readunit = splitNumUnit(aread)
        read = float(read)
        readstatus,readunit = readunit[0],readunit[1:]
        #print read, readstatus, readunit
        tstformat = "%H:%M:%S.%f,%d-%b-%Y"
        tst = datetime.datetime.strptime(atime + "," + adate, tstformat)
        #print tst
        rnum,rnumunit = splitNumUnit(arnum)
        rnum = int(rnum)
        #print rnum, rnumunit
        vso,vsounit = None,None
        #print vso, vsounit

    result = readStruct(read,readstatus,readunit,tst,rnum,vso,vsounit)
    if recurse:
        return result, tail
    else:
        return result

def parseTraceData(format_flags, s):
    aseq = []
    while len(s):
        head,s = parseRead(format_flags, s, True)
        aseq.append(head)
    #print aseq
    #print s
    return aseq

"""
    Unit tests!
"""

def unitTestParseRead():
    # See the :FORMat:ELEMents command, page 14-36
    # Example output looks like this:
    rx_read = \
        "+01.01103E+00NVDC,09:00:20.00,26-Mar-2015,+01945RDNG#,+0001.000Vsrc"
    print("Imagine: tx> {}".format(defaultFormat.getFormatCommand()))
    print("Imagine: tx> :READ?")
    print("Imagine: rx< {}".format(rx_read))
    print(parseRead(defaultFormat,rx_read))
    print()
    
def unitTestParseSeqData():
    # However, when running a sequence mode, the VSO is ommitted, like:
    example_read_seq = "+00.00849E+00NVDC,09:43:20.00,26-Mar-2015,+00000RDNG#"
    print("Imagine: tx> {}".format(seqFormat.getFormatCommand()))
    print("Imagine: tx> :TRACE:DATA?")
    print("Imagine: rx< {}".format(example_read_seq))
    print(parseTraceData(seqFormat, ",".join([example_read_seq,] * 4)))
    print()

def main():
    unitTestParseRead()
    unitTestParseSeqData()

if __name__ == "__main__":
    main()
    
