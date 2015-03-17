# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 14:44:29 2014

@author: nfette
"""

import binascii
import string
import struct
import datetime
import xml.etree.ElementTree as ET

K_headfmt = '>xxxHHBBB'
K_tailfmt = 'xxH'
K_headerlength = struct.calcsize(K_headfmt) # 10
K_footerlength = struct.calcsize(K_tailfmt) # 4
K_eachfmt = '<L'
K_eachlength = struct.calcsize(K_eachfmt) # 4
Jcommand_header = '\x00\x60\x00\x00'

def convertFromCSIFPF(bytes):
    isNegative = 0x80 & bytes[0]
    sign = -1. if isNegative else 1.
    exponent = (0x7F & bytes[0]) - 0x40
    mantissaNumer = (2<<16) * bytes[1] + (2<<8) * bytes[2] + bytes[3]
    mantissaDenom = (2<<24)
    mantissa = (mantissaNumer) * (1. / mantissaDenom)
    result = sign * mantissa * pow(2,exponent)
    return result

def calcKmessageLength(nlocs):
    return K_headerlength + nlocs * K_eachlength + K_footerlength

def translateK(msg, nlocs=-1):
    length = len(msg)

    datalength = length - (K_headerlength + K_footerlength)
    nlocsExpected = datalength / 4
    # check if the message is the correct length?
    if nlocs < 0:
        nlocs = nlocsExpected
    else:
        if nlocs != nlocsExpected:
            raise Exception("CR23x K command: expected different number of fields")
    datafmt = '<{}L'.format(nlocs)
    
    header = struct.unpack(K_headfmt,msg[0:K_headerlength])
    data1 = bytearray(msg[K_headerlength:K_headerlength+datalength])
    tail = struct.unpack(K_tailfmt,msg[K_headerlength+datalength:])
    
    # oddly, the time stamp in the message header does not include date.
    timeHours = header[0] / 60
    timeMins = header[0] % 60
    timeSecs = header[1] / 10
    timeMicros = 100000 * (header[1] % 10)
    t = datetime.time(hour=timeHours, minute=timeMins, second=timeSecs, microsecond=timeMicros)
    # I just throw out the rest of the header
    flags1to8 = header[2]
    ports = header[3]
    flags11to18 = header[4]
    # Now the actual fields
    data2 = [data1[4*i:4*i+4] for i in range(nlocs)]
    data3 = map(convertFromCSIFPF, data2)
    
    return t, data3

def testTranslateK():
    # An example input
    msg = binascii.unhexlify(string.replace(
    '4B 0D 0A 04 27 00 B3 00 00 00 44 CE 0B 9B 00 00 00 00 45 B2 AB 48 45 A8 E2 F0 45 A6 89 70 45 A3 56 77 45 A3 45 BE 45 9D 00 52 45 98 3A BB 45 8A E1 3F 45 8A 28 CF 7F 00 57 8A',' ',''))
    t, data3 = translateK(msg)
    print t
    print data3
    
def getLabels(filenameSCW):
    tree = ET.parse(filenameSCW);
    root = tree.getroot();
    inlocstringlist=root.find('scprogram').find('inlocstringlist')
    labels=[s.text.split(',')[1] for s in inlocstringlist.getchildren()]
    return labels

def testGetLabels():
    programFilename = 'cr23x_programs/wind_tunnel_8channels.scw'
    labels = getLabels(programFilename)
    print labels
    
if __name__ == '__main__':    
    testGetLabels()
    testTranslateK()
    
    
