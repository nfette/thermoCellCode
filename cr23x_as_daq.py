# -*- coding: utf-8 -*-
"""
This is the code for retrieving CR23x samples approximately every second.
This does not prevent the CR23x from recording the usual "final storage" data
at 1 minute intervals. However, you should not attempt to connect to the CR23x
via another program while this one is running.

To stop collecting samples, simply press Ctrl-C in the shell window.
"""

import serial
import time
import datetime
import binascii
import string
import os
import itertools

import libcr23x
import siteDefs


programFilename = 'cr23x_programs/wind_tunnel_9channels.scw'
timeStamp = datetime.datetime.now()
timeStampStr = timeStamp.isoformat().replace(':','=')
basename = "cr23x_outputs_"
outputFilename = "{}{}{}.dat".format(siteDefs.data_base_dir, basename, timeStampStr)
port = 'com3'

if not os.path.isfile(outputFilename):
    print("Creating {} for headers and data".format(outputFilename))
    with open(outputFilename,'w') as f:
        labels = libcr23x.getLabels(programFilename)
        nlocs = len(labels)
        labels = ['ComputerTime','TimeStamp']+labels
        f.write(','.join(labels) + '\n')
else:
    print("Opening {} and appending data".format(outputFilename))

with serial.Serial(port=port, baudrate=9600,
                   timeout=2, writeTimeout=2) as ser,\
                   open(outputFilename,'a') as f:
    try:
        while (ser.inWaiting() < 3):
            print "Tx knock"
            ser.write('\r')
            time.sleep(0.1) # this is key! responder waits for a pause
        a = ser.read(3)
        print "Rx come in"
                
        print "Tx time?"
        ser.write('C\r')
        time.sleep(0.2)
        b = ser.read(67)
        b1,b2=b[4:24],b[25:30]
        dt = datetime.datetime.strptime(b1, 'Y%y D0%j  T%H:%M:%S')
        print "Rx the time is", dt
        print "   and a number is", b2
        
        print "Tx any new numbers for me?"
        ser.write('A\r')
        time.sleep(0.2)
        c = ser.read(157)
        print c
        
        print "Tx I'd like to ask about the current numbers."
        ser.write('2413J\r')
        j1 = ser.read(8)
        print j1
        ser.write(libcr23x.Jcommand_header + chr(0))
        j2 = ser.read(5)
        print binascii.hexlify(j2)
        ser.write('K\r')
        time.sleep(2)
        j3 = ser.read(20) # maybe wait for this one
        print binascii.hexlify(j3)
        ser.write('2413J\r')
        j4 = ser.read(8)
        print j4
        # TODO: This should depend on the number of input locations in the program
        Jcommand_locations = ''.join(map(chr, range(1,1+nlocs)))
        Jcommand = libcr23x.Jcommand_header + Jcommand_locations + chr(0);
        ser.write(Jcommand)
        # Confirmation
        j5 = ser.read(len(Jcommand))
        print binascii.hexlify(j5)
        
        try:
            for n in itertools.count():
                print "[{}] Tx hey what are the numbers now?".format(n)
                ser.write('K\r')
                expectedBytes = libcr23x.calcKmessageLength(nlocs) # eg 58 for 11 fields
                d = ser.read(expectedBytes)
                dhex = binascii.hexlify(d)
                #print " ".join(dhex[2*i:(2*i+2)] for i in range(58))
                # now we must parse this per appendix C of cr23x manual
                t,data3 = libcr23x.translateK(d, nlocs)
                data4 = [t.isoformat()]+map(str,data3)
                tcomputer = datetime.datetime.now().isoformat()
                data5 = [tcomputer] + data4
                f.write(','.join(data5) + '\n')
                time.sleep(0.8)
        except KeyboardInterrupt:
            pass
        
        print "Tx let's finish"
        ser.write('E')
        ser.read()
        print "Rx ok"
        print "Tx bye"
        ser.write('\r')
        ser.read()
        print "Rx bye bye"
    except serial.SerialException as e:
        print e
        raise
