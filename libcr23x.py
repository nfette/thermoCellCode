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

def convertFromCSIFPF(bytes):
    isNegative = 0x80 & bytes[0]
    sign = -1. if isNegative else 1.
    exponent = (0x7F & bytes[0]) - 0x40
    mantissaNumer = (2<<16) * bytes[1] + (2<<8) * bytes[2] + bytes[3]
    mantissaDenom = (2<<24)
    mantissa = (mantissaNumer) * (1. / mantissaDenom)
    result = sign * mantissa * pow(2,exponent)
    return result

def translateK(msg):
    length = len(msg)
    headerlength = 10
    footerlength = 4
    datalength = length - headerlength - footerlength
    nlocs = datalength / 4
    headfmt = '>xxxHHBBB'
    datafmt = '<' + str(nlocs) + 'L'
    # check if the message is the correct length?
    tailfmt = 'xxH'
    header = struct.unpack(headfmt,msg[0:headerlength])
    data1 = bytearray(msg[headerlength:headerlength+datalength])
    tail = struct.unpack(tailfmt,msg[headerlength+datalength:])
    
    timeHours = header[0] / 60
    timeMins = header[0] % 60
    timeSecs = header[1] / 10
    timeMicros = 100000 * (header[1] % 10)
    t = datetime.time(hour=timeHours, minute=timeMins, second=timeSecs, microsecond=timeMicros)
    flags1to8 = header[2]
    ports = header[3]
    flags11to18 = header[4]
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
    programFilename = 'wind_tunnel_8channels.scw'
    labels = getLabels(programFilename)
    print labels
    
if __name__ == '__main__':    
    testGetLabels()
    testTranslateK()
    
    