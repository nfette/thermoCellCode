# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import serial
import time
import datetime
import binascii
import string
import libcr23x
import os
import siteDefs

programFilename = 'cr23x_programs/wind_tunnel_8channels.scw'
outputFilename = siteDefs.data_base_dir + "myoutputs.dat"
port = 'com3'

if not os.path.isfile(outputFilename):
    with open(outputFilename,'w') as f:
        labels = libcr23x.getLabels(programFilename)
        labels = ['TimeStamp']+labels
        f.write(','.join(labels))

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
        ser.write('\x00\x60\x00\x00\x00')
        j2 = ser.read(5)
        print binascii.hexlify(j2)
        ser.write('K\r')
        time.sleep(2)
        j3 = ser.read(20) # maybe wait for this one
        print binascii.hexlify(j3)
        ser.write('2413J\r')
        j4 = ser.read(8)
        print j4
        ser.write(binascii.unhexlify(
            string.replace('00 60 00 00 01 02 03 04 05 06 07 08 09 0A 0B 00',' ','')))
        j5 = ser.read(16)
        print binascii.hexlify(j5)
        
        for n in range(100):
            print "Tx hey what are the numbers now?"
            ser.write('K\r')
            d = ser.read(58)
            dhex = binascii.hexlify(d)
            #print " ".join(dhex[2*i:(2*i+2)] for i in range(58))
            # now we must parse this per appendix C of cr23x manual
            t,data3 = libcr23x.translateK(d)
            data4 = [t.isoformat()]+map(str,data3)
            f.write(','.join(data4) + '\n')
            time.sleep(1)
        
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
