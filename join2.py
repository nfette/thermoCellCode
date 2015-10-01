"""
join2.py

==Description==
Measurement:
    N/A
Inputs:
    The text data files created by uniforms.py, or binary shadow copies created
    by this program. (Delete these to re-create them.)
Post-processing:
    Calculations and plots of electrical data from select thermocell trials.

==Change log==
    2015-09-29, created by Nicholas Fette
"""

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

import siteDefs
import os
import datetime
import numpy as np
import itertools
import pickle
import matplotlib.pyplot as plt
import join2types
import matplotlib.dates as mdates
import pytz

# Where did we collect the data? Forgot to put timezone in curve trace files.
tz = pytz.timezone('US/Arizona')

dtype2=[('ComputerTime','<M8[us]'),
        ('Voltage','<f8'),
        ('Vsource','<f8'),
        ('Rsensor','<f8'),
        ('Rbypass','<f8'),
        ('OCcount','<i4')]

dtype3=[('ComputerTime','<M8[us]'),
        ('PTemp_C','<f8'),
        ('T_gun_1','<f8'),
        ('T_gun_2','<f8'),
        ('T_h_dry','<f8'),
        ('T_h_wet','<f8'),
        ('T_c_wet','<f8'),
        ('T_c_dry','<f8'),
        ('T_amb_1','<f8'),
        ('T_amb_2','<f8'),
        ('T_fintip','<f8')]
usecols3=[0,4,5,6,7,8,9,10,11,12,13]

todolist = [('2015-09-10T21=46=34.891000.dat','cr23x_outputs_2015-09-10T21=34=56.579000.dat',
               [('2015-09-11T02:10:00.000000','2015-09-11T03:20:00.000000'),
                ('2015-09-11T13:40:00.000000','2015-09-11T14:20:00.000000'),
                ('2015-09-11T19:30:00.000000','2015-09-11T21:25:00.000000'),
                ('2015-09-12T13:00:00.000000','2015-09-12T13:32:00.000000')]),
            ('2015-09-13T18=38=23.924000.dat','cr23x_outputs_2015-09-13T19=49=03.865000.dat',
               [('2015-09-14T13:00:00.000000','2015-09-14T14:26:00.000000'),
                ('2015-09-14T20:00:00.000000','2015-09-14T21:50:00.000000'),
                ('2015-09-15T10:20:00.000000','2015-09-15T12:10:00.000000'),
                ('2015-09-15T16:00:00.000000','2015-09-15T19:40:00.000000')]),
            ('2015-09-21T20=30=53.154000.dat','cr23x_outputs_2015-09-21T20=21=39.466000.dat',
               [('2015-09-22T11:00:00.000000','2015-09-22T13:00:00.000000'),
                ('2015-09-22T15:30:00.000000','2015-09-22T16:30:00.000000'),
                ('2015-09-22T20:00:00.000000','2015-09-22T21:00:00.000000'),
                ('2015-09-22T23:00:00.000000','2015-09-23T00:00:00.000000')]),
            ('2015-09-23T09=46=55.059000.dat','cr23x_outputs_2015-09-23T10=00=56.923000.dat',
               [('2015-09-23T14:00:00.000000','2015-09-23T15:00:00.000000'),
                ('2015-09-23T17:40:00.000000','2015-09-23T18:40:00.000000'),
                ('2015-09-23T20:30:00.000000','2015-09-23T21:30:00.000000'),
                ('2015-09-24T00:30:00.000000','2015-09-24T01:30:00.000000')]),
            ('2015-09-24T11=13=51.022000.dat','cr23x_outputs_2015-09-24T10=40=18.244000.dat',
               [('2015-09-24T16:10:00.000000','2015-09-24T17:10:00.000000'),
                ('2015-09-24T19:30:00.000000','2015-09-24T20:30:00.000000'),
                ('2015-09-24T22:10:00.000000','2015-09-24T23:10:00.000000'),
                ('2015-09-25T02:10:00.000000','2015-09-25T03:10:00.000000')]),
            ]

masks = [('2015-09-11T19:49:10.193000','2015-09-11T19:50:30.045000'),
         ('2015-09-11T20:06:44.344000','2015-09-11T20:08:05.056000'),
         ('2015-09-11T20:11:10.040000','2015-09-11T20:11:30.000000'),
         ('2015-09-11T20:12:58.712000','2015-09-11T20:14:28.044000'),
         ('2015-09-11T21:20:33.491000','2015-09-11T21:21:30.082000'),
         ('2015-09-11T21:22:28.863000','2015-09-11T21:23:00.014000')
         ]

fun = lambda(s):np.datetime64(tz.localize(datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S.%f")))

def getCellDataNames(fname):
    uniformName = "{}{}{}".format(
        siteDefs.data_base_dir,"uniform_data/",fname)
    uniformPickle = "{}{}{}".format(
        siteDefs.data_base_dir,"uniform_data/",os.path.splitext(fname)[0] + '.pkl')
    return uniformName, uniformPickle

def getFigname(fname):
    figname = "{}{}{}".format(
        siteDefs.data_base_dir,"uniform_data/",os.path.splitext(fname)[0] + '.fig1.png')
    return figname

def getThermalDataName(fname):
    thermalFileName = "{}{}{}".format(
        siteDefs.data_base_dir,"temperature_data/",fname)
    return thermalFileName

def fetchCellData(fname):
    # Read the data
    uniformName, uniformPickle = getCellDataNames(fname)
    
    try:
        with open(uniformPickle,'rb') as f:
            tup = pickle.load(f)
            t,Vcell,I,P = tup
    except:        
        print "Reading the file. This may take a little while."
        uData = np.genfromtxt(uniformName, delimiter=",", names=True,
                     dtype=dtype2)
        t = uData['ComputerTime']
        Vsrc = uData['Vsource']
        Vread = uData['Voltage']
        Rsensor = uData['Rsensor']
        Rbypass = uData['Rbypass']
        Vcell = -Vread
        Vsens = Vsrc - Vread
        I = Vsens / Rsensor + Vcell/Rbypass
        P = Vcell * I
        with open(uniformPickle,'wb') as f:
            pickle.dump(join2types.uDataType(t,Vcell,I,P),f)
    return t, Vcell, I, P

def fetchThermalData(fname):
    thermalFileName = getThermalDataName(fname)
    # Read the data
    thermalData = np.genfromtxt(thermalFileName,delimiter=",", names=True,
                                dtype=dtype3, usecols=usecols3)
    return thermalData

def plotStuff(t,Vcell,I,P,t3,thermalData):
    fig, (row1, row2) = plt.subplots(2,2,sharex='col',figsize=(16,8))
    ax0,ax1 = row1
    ax2,ax3 = row2

    for aName,aType in dtype3[1:]:
        ax0.plot(t3,thermalData[aName],label=aName)
    #ax0.legend()
        
    ax1.plot(Vcell,P,'o')
    ax1.set_ylabel('Power')
    ax1.set_xlabel('Voltage')

    ax2.plot(t,Vcell,'r.',label="Voltage")
    ax2b = ax2.twinx()
    #ax2c = ax2.twinx()
    ax2b.plot(t,I,'g.',label="Current")
    #ax2c.plot(t,P,'b.',label="Power")
    ax2.grid(True,which='both',axis='both')
    ml=mdates.MinuteLocator(byminute=range(0,60,5),tz=tz)
    ax2.xaxis.set_major_locator(ml)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M",tz=tz))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=20,
          horizontalalignment='right' )
    fig.autofmt_xdate()
    
    ax3.plot(Vcell,I,'o')
    ax3.set_ylabel('Current')
    ax3.set_xlabel('Voltage')
    ax3.grid(True,which='both',axis='both')

def main1():
    for cellFilename,thermalFilename,intervals in todolist:
        #figname = getFigname(cellFilename)
        #if os.path.exists(figname):
        #    continue
        
        print "Read cell data for trial: {}".format(cellFilename)
        tCell, Vcell, I, P = fetchCellData(cellFilename)
        print "Read thermal data for trial: {}".format(thermalFilename)
        thermalData = fetchThermalData(thermalFilename)
        tThermal=thermalData['ComputerTime']

        for startst,stopst in intervals:
            figname = getFigname(startst.replace(":","="))
            if os.path.exists(figname):
               continue
            start,stop = fun(startst), fun(stopst)
            indicesCell = np.logical_and(start <= tCell, tCell < stop)
            t2 = tCell[indicesCell].astype(datetime.datetime)
            indicesThermal = np.logical_and(start <= tThermal, tThermal < stop)
            t3 = tThermal[indicesThermal].astype(datetime.datetime)
            plotStuff(t2,Vcell[indicesCell],I[indicesCell],P[indicesCell],
                      t3,thermalData[indicesThermal])
            plt.savefig(figname)
            #plt.show()
            plt.close()
        
if __name__ == "__main__":
    main1()
    
