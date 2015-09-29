# 2015-09-10
# Trial 1, CuSO4 with plain surface electrodes
# open_circuit_voltage/2015-09-10T21=46=34.891000.dat
# curve_traces/2015-09-11T02=17=58.551000.pkl
# ...
# curve_traces/2015-09-13T14=12=55.787000.pkl
# 
# Events:
# 2015-09-11T19:49:10.193000: bypass insert 1 ohm nominal
# 2015-09-11T20:06:44.344000: bypass insert 1/2 ohm nominal
# 2015-09-11T20:11:10.040000: bypass insert 1/3 ohm nominal
# 2015-09-11T20:12:58.712000: bypass removed
# 2015-09-11T21:20:33.491000: bypass insert 1 ohm nominal
# 2015-09-11T21:22:28.863000: bypass insert 1/2 ohm nominal
# 2015-09-11T21:26:20.774000: bypass removed

# 2015-09-13
# Trial 2, CuSO4 with plain surface electrodes
# open_circuit_voltage/2015-09-13T18=38=23.924000.dat
# curve_traces/2015-09-13T18=38=25.084000.pkl
# ...
# curve_traces/2015-09-15T19=57=41.305000.pkl
# 
# Events:
# 2015-09-14T13:40:50.902000: bypass insert some ohms
# 2015-09-14T14:27:13.511000: bypass removed
# 2015-09-14T21:00:49.471000: bypass insert some ohms
# 2015-09-14T21:13:59.229000: bypass change some ohms
# 2015-09-14T21:54:32.021000: bypass removed
# 2015-09-15T11:33:22.671000: bypass insert some ohms
# 2015-09-15T12:10:46.193000: bypass removed
# 2015-09-15T17:29:54.549000: bypass insert some ohms
# 2015-09-15T19:02:50.123000: bypass removed

# 2015-09-21
# Trial 1, Cu+EDTA with grooved surface hot electrode
# open_circuit_voltage/2015-09-21T20=30=53.154000.dat

# 2015-09-23
# Trial 1, CuSO4 with grooved surface hot electrode
# open_circuit_voltage/2015-09-23T09=46=55.059000.dat
# Events:
# 2015-09-23T10:21:39.404000: switched polarity of cell

# 2015-09-24
# Trial 2, CuSO4 with grooved surface hot electrode
# open_circuit_voltage/2015-09-24T11=13=51.022000.dat
# Events:
# Nothing interesting

from libkeithley6517b import pvpanelType
import keithley6517b_delta
import unpickletest2
import siteDefs
import os
import datetime
import numpy as np
from collections import namedtuple
import pickle
from joinData1 import filename2timestamp, getCurveTraceTimes
import itertools
import pytz
import json

# Where did we collect the data? Forgot to put timezone in curve trace files.
tz = pytz.timezone('US/Arizona')

dtype1='<M8[us],<f8,S3'
dtype2=[('ComputerTime','<M8[us]'),
        ('Voltage','<f8'),
        ('Vsource','<f8'),
        ('Rsensor','<f8'),
        ('Rbypass','<f8'),
        ('OCcount','<i4')]
        
# Old heterogenous databases
# For these files, need to:
# 1. Generate time stamps for all data points within each curve trace
# 2. Stitch together the open circuit files and curve traces files.
# 3. Add data about bypass resistor
# 4. Save the data.
todolist = [('open_circuit_voltage/2015-09-13T18=38=23.924000.dat',
             datetime.datetime(2015,9,13,18,38,23),
             datetime.datetime(2015,9,15,19,57,41)),
            ('open_circuit_voltage/2015-09-10T21=46=34.891000.dat',
             datetime.datetime(2015,9,11,2,17,58),
             datetime.datetime(2015,9,13,14,12,56))]
# Need to record the bypass resistor history.
resFile = "IVconfigs/resistors.txt"
with open(resFile,'r') as fres:
    resistors = json.load(fres)
bpKey = ["2015-09-11T19:49:10.193000",
    "2015-09-11T20:06:44.344000",
    "2015-09-11T20:11:10.040000",
    "2015-09-11T20:12:58.712000",
    "2015-09-11T21:20:33.491000",
    "2015-09-11T21:22:28.863000",
    "2015-09-11T21:26:20.774000",
    "2015-09-14T13:40:50.902000",
    "2015-09-14T14:27:13.511000",
    "2015-09-14T21:00:49.471000",
    "2015-09-14T21:13:59.229000",
    "2015-09-14T21:54:32.021000",
    "2015-09-15T11:33:22.671000",
    "2015-09-15T12:10:46.193000",
    "2015-09-15T17:29:54.549000",
    "2015-09-15T19:02:50.123000"]
fun = lambda(s):np.datetime64(tz.localize(datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S.%f")))
bpKey = map(fun,bpKey)
bypassIntervals=[(bpKey[0],bpKey[1],"bypass_single"),
                 (bpKey[1],bpKey[2],"bypass_parallel_2"),
                 (bpKey[2],bpKey[3],"bypass_parallel_3"),
                 (bpKey[4],bpKey[5],"bypass_single"),
                 (bpKey[5],bpKey[6],"bypass_parallel_2"),
                 (bpKey[7],bpKey[8],"bypass_single"),
                 (bpKey[9],bpKey[10],"bypass_single"),
                 (bpKey[10],bpKey[11],"bypass_parallel_2"),
                 (bpKey[12],bpKey[13],"bypass_single"),
                 (bpKey[14],bpKey[15],"bypass_single"),
                 ]

def main1():
    # Collect stats about Keithley's staircase sweep timing
    tSample1 = []
    tSampleD = []
    
    for (ocFile, traceStart, traceStop) in todolist:
        print "Merging data for trial: {}".format(ocFile)

        # Read the ocFile
        ocfname = "{}{}".format(siteDefs.data_base_dir,ocFile)
        uniformName = "{}{}{}".format(
            siteDefs.data_base_dir,"uniform_data/",os.path.basename(ocFile))
        
        print "Reading the file. This may take a little while."
        ocDataRaw = np.genfromtxt(ocfname, delimiter=",", names=True,
                     dtype=dtype1)
        print "Allocating new array."
        ocData = np.zeros(len(ocDataRaw),dtype=dtype2)
        ocData['ComputerTime'] = ocDataRaw['ComputerTime']
        ocData['Voltage'] = ocDataRaw['Voltage']
        ocData['Rsensor'] = 1e300
        ocData['Rbypass'] = 1e300
        ocData['OCcount'] = 1

        # Get the list of curve trace files
        print "Searching for curve trace files ..."
        times = getCurveTraceTimes(traceStart,traceStop)
        print "Found {} curve trace files.".format(len(times))
        
        print "Reading curve trace files. This may take a few moments..."
        stims = []
        
        for (i, time) in zip(itertools.count(), times):
            outputPickle, outputPlot = keithley6517b_delta.picklePlotFileNames(time)
            with open(outputPickle,'r') as f:
                data = pickle.load(f)
            # start, stop, step, stim, nfields
            npoints = 1+(data.stop-data.start)/data.step
            Vin = np.linspace(data.start,data.stop,npoints)
            Vout, tSample, iSample = data.data.T
            # Do some consistency checking
            stims.append(data.stim)
            badVal = -999
            if badVal in tSample:
                # We need to generate timestamps because Keithley was bad
                tSample = np.arange(npoints - 1)
                # Use here the results printed out below
                tSample = tSample1Mean + tSampleDMean * tSample
                tSample = np.concatenate([[0],tSample])
            else:
                deltatSample = np.diff(tSample)
                tSample1.append(deltatSample[0])
                tSampleD.append(deltatSample[1:].mean())
            
            if npoints != len(Vout):
                print "At {}, mismatch of data".format(time)
            if not i%100:
                print "{} and counting".format(i)

            curveTraceToAdd = np.zeros(npoints,dtype=dtype2)
            tplus = tz.localize(time)
            tSample4Me = np.repeat(np.array(tplus,dtype='datetime64[us]'),npoints)\
                + np.array(100000*tSample,dtype='timedelta64[us]')
            curveTraceToAdd['ComputerTime']=tSample4Me
            curveTraceToAdd['Voltage']=Vout
            curveTraceToAdd['Vsource']=Vin
            curveTraceToAdd['Rsensor']=data.r_current_sensor
            curveTraceToAdd['Rbypass']=1e300

            ocData = np.concatenate([ocData,curveTraceToAdd])

        print "Done looping through all the curve trace files."
        tSample1Mean,tSampleDMean = np.mean(tSample1),np.mean(tSampleD)
        print "tSample1Mean = {}".format(tSample1Mean)
        print "tSampleDMean = {}".format(tSampleDMean)
        print "min(stims) = {}".format(min(stims))
        print "max(stims) = {}".format(max(stims))

        # Input the bypass resistor info.
        for (bpStart, bpStop, bpTag) in bypassIntervals:
            tcheck = np.logical_and(bpStart <= ocData['ComputerTime'],
                                    ocData['ComputerTime'] < bpStop)
            ocData['Rbypass'][tcheck] = resistors[bpTag]

        print "Writing the uniform file: {}".format(uniformName)
        ocData.sort()
        with open(uniformName,'w') as f:
            f.write("{}\n".format(",".join(ocData.dtype.names)))
            for row in ocData:
                f.write("{}\n".format(','.join([i.__str__() for i in row])))
        print "Done with that."


# Newer homogeneous databases
# For these, we just need to
# 1. Overwrite the time stamp with time zone info for easy reading
# 2. Overwrite resistor values with more accurate measurements
# 3. Deduce the starting points for all the curve traces.
# 4. Save the data.
todolist2 = ["2015-09-21T20=30=53.154000.dat",
    "2015-09-23T09=46=55.059000.dat",
    "2015-09-24T11=13=51.022000.dat"]

polKeys=map(fun,
            ["2015-09-23T09:46:55.059000",
             "2015-09-23T10:21:39.404000"])

    
if __name__ == "__main__":
    #main1()
    for ocFile in todolist2:
        ocfname = "{}{}{}".format(siteDefs.data_base_dir,"open_circuit_voltage/",ocFile)
        uniformName = "{}{}{}".format(
            siteDefs.data_base_dir,"uniform_data/",ocFile)
        print "Correcting data for trial: {}".format(ocFile)
        print "Reading the file. This may take a little while."
        ocData = np.genfromtxt(ocfname, delimiter=",", names=True, dtype=dtype2)
        Rbypass_seen = set()
        for r in ocData['Rbypass']:
            Rbypass_seen.add(r)
        Rsensor_seen = set()
        for r in ocData['Rsensor']:
            Rsensor_seen.add(r)
        print "Saw these values of bypass: ", Rbypass_seen
        print "Saw these values of sensor: ", Rsensor_seen
        # Fix em up
        whenSens1 = ocData['Rsensor'] == 98.3
        whenSens2 = ocData['Rsensor'] == 972.0
        whenSens3 = ocData['Rsensor'] == 4612.0
        whenBypass1 = ocData['Rbypass'] == 1.0
        ocData['Rsensor'][whenSens1] = resistors['current_sensor_1']
        ocData['Rsensor'][whenSens2] = resistors['current_sensor_2']
        ocData['Rsensor'][whenSens3] = resistors['current_sensor_3']
        ocData['Rbypass'][whenBypass1] = resistors['bypass_single']
        # Switch the wires back
        whenSwapPolarity = np.logical_and(polKeys[0] < ocData['ComputerTime'],
                                          ocData['ComputerTime'] < polKeys[1])
        ocData['Voltage'][whenSwapPolarity] *= -1
        
        print "Writing the uniform file: {}".format(uniformName)
        with open(uniformName,'w') as f:
            f.write("{}\n".format(",".join(ocData.dtype.names)))
            for row in ocData:
                f.write("{}\n".format(','.join([i.__str__() for i in row])))
        print "Done with that."
