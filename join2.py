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

todolist = [('CuSO$_4$, plain surface, trial 1',
             '2015-09-10T21=46=34.891000.dat','cr23x_outputs_2015-09-10T21=34=56.579000.dat',
               [('setpoint A','2015-09-11T02:10:00.000000','2015-09-11T03:20:00.000000'),
                ('setpoint B','2015-09-11T13:40:00.000000','2015-09-11T14:20:00.000000'),
                ('setpoint C','2015-09-11T19:30:00.000000','2015-09-11T21:25:00.000000'),
                ('setpoint D','2015-09-12T13:00:00.000000','2015-09-12T13:32:00.000000')]),
            ('CuSO$_4$, plain surface, trial 2',
             '2015-09-13T18=38=23.924000.dat','cr23x_outputs_2015-09-13T19=49=03.865000.dat',
               [('setpoint C','2015-09-14T13:00:00.000000','2015-09-14T14:26:00.000000'),
                ('setpoint A','2015-09-14T20:00:00.000000','2015-09-14T21:50:00.000000'),
                ('setpoint C','2015-09-15T10:20:00.000000','2015-09-15T12:10:00.000000'),
                ('setpoint B','2015-09-15T16:00:00.000000','2015-09-15T19:40:00.000000')]),
            ('Cu+EDTA, grooved surface, trial 1',
             '2015-09-21T20=30=53.154000.dat','cr23x_outputs_2015-09-21T20=21=39.466000.dat',
               [('setpoint D','2015-09-22T11:00:00.000000','2015-09-22T13:00:00.000000'),
                ('setpoint A','2015-09-22T15:30:00.000000','2015-09-22T16:30:00.000000'),
                ('setpoint B','2015-09-22T20:00:00.000000','2015-09-22T21:00:00.000000'),
                ('setpoint C','2015-09-22T23:00:00.000000','2015-09-23T00:00:00.000000')]),
            ('CuSO$_4$, grooved surface, trial 1',
             '2015-09-23T09=46=55.059000.dat','cr23x_outputs_2015-09-23T10=00=56.923000.dat',
               [('setpoint D','2015-09-23T14:00:00.000000','2015-09-23T15:00:00.000000'),
                ('setpoint A','2015-09-23T17:40:00.000000','2015-09-23T18:40:00.000000'),
                ('setpoint C','2015-09-23T20:30:00.000000','2015-09-23T21:30:00.000000'),
                ('setpoint C','2015-09-24T00:30:00.000000','2015-09-24T01:30:00.000000')]),
            ('CuSO$_4$, grooved surface, trial 2',
             '2015-09-24T11=13=51.022000.dat','cr23x_outputs_2015-09-24T10=40=18.244000.dat',
               [('setpoint D','2015-09-24T16:10:00.000000','2015-09-24T17:10:00.000000'),
                ('setpoint A','2015-09-24T19:30:00.000000','2015-09-24T20:30:00.000000'),
                ('setpoint B','2015-09-24T22:10:00.000000','2015-09-24T23:10:00.000000'),
                ('setpoint C','2015-09-25T02:10:00.000000','2015-09-25T03:10:00.000000')]),
            ]

masks = [('2015-09-11T19:49:10.193000','2015-09-11T19:50:30.045000'),
         ('2015-09-11T20:06:44.344000','2015-09-11T20:08:05.056000'),
         ('2015-09-11T20:11:10.040000','2015-09-11T20:11:30.000000'),
         ('2015-09-11T20:12:58.712000','2015-09-11T20:14:28.044000'),
         ('2015-09-11T21:20:33.491000','2015-09-11T21:21:30.082000'),
         ('2015-09-11T21:22:28.863000','2015-09-11T21:23:00.014000'),
         \
         ('2015-09-14T13:40:00.000000','2015-09-14T13:43:00.000000'),
         ('2015-09-14T21:00:00.000000','2015-09-14T21:02:00.000000'),
         ('2015-09-14T21:12:00.000000','2015-09-14T21:15:00.000000'),
         ('2015-09-15T11:33:00.000000','2015-09-15T11:35:00.000000'),
         ('2015-09-15T17:25:00.000000','2015-09-15T17:35:00.000000'),
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
            t,Vcell,I,P,OCcount = tup
    except:        
        print "Reading the file. This may take a little while."
        uData = np.genfromtxt(uniformName, delimiter=",", names=True,
                     dtype=dtype2)
        t = uData['ComputerTime']
        Vsrc = uData['Vsource']
        Vread = uData['Voltage']
        Rsensor = uData['Rsensor']
        Rbypass = uData['Rbypass']
        OCcount = uData['OCcount']
        Vcell = -Vread
        Vsens = Vsrc - Vread
        I = Vsens / Rsensor + Vcell/Rbypass
        P = Vcell * I
        with open(uniformPickle,'wb') as f:
            pickle.dump(join2types.uDataType(t,Vcell,I,P,OCcount),f)
    return t, Vcell, I, P, OCcount

def fetchThermalData(fname):
    thermalFileName = getThermalDataName(fname)
    # Read the data
    thermalData = np.genfromtxt(thermalFileName,delimiter=",", names=True,
                                dtype=dtype3, usecols=usecols3)
    return thermalData

def plotStuff(t,Vcell,I,P,mask,t3,thermalData,label):
    fig, (row1, row2) = plt.subplots(2,2,sharex='col',figsize=(16,8))
    ax0,ax1 = row1
    ax2,ax3 = row2
    fig.suptitle(label)
    
    for aName,aType in dtype3[1:]:
        ax0.plot(t3,thermalData[aName],label=aName)
    #ax0.legend()
    ax0.set_ylim([0,120])
    ax0.set_ylabel('Temperature [$^\circ$C]')
    ax0.grid(True,which='both',axis='both')

    ax1.plot(1e3*Vcell[mask],1e6*P[mask],'o')
    ax1.set_ylabel('Power / $\mu$W')
    ax1.set_xlabel('Voltage / mV')
    ax1.grid(True,which='both',axis='both')

    ax2.plot(t,1e3*Vcell,'r.',label="Voltage / mV")
    #ax2.set_ylim([-20,200])
    ax2b = ax2.twinx()
    #ax2c = ax2.twinx()
    ax2b.plot(t,1e3*I,'g.',label="Current / mA")
    #ax2c.plot(t,P,'b.',label="Power")
    ax2.grid(True,which='both',axis='both')
    ml10=mdates.MinuteLocator(byminute=range(0,60,5),tz=tz)
    ml10=mdates.MinuteLocator(byminute=range(0,60,10),tz=tz)
    ax2.xaxis.set_major_locator(ml10)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M",tz=tz))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=20,
          horizontalalignment='right' )
    fig.autofmt_xdate()
    
    ax3.plot(1e3*Vcell[mask],1e3*I[mask],'o')
    ax3.set_ylabel('Current / mA')
    ax3.set_xlabel('Voltage / mV')
    ax3.grid(True,which='both',axis='both')

def plotAllTogether(fig,ax1,ax2,Vcell,I,P,mask,label,n=4):
    if not fig:
        #fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,sharex='col',figsize=(6,20))
        fig = plt.figure(figsize=(6,5*n))
        ax1 = fig.add_subplot(n,1,1)
        ax2 = fig.add_subplot(n,1,2)
        ax1.set_xlabel('Voltage / mV')
        ax1.set_ylabel('Power / $\mu$W')
        ax2.set_xlabel('Voltage / mV')
        ax2.set_ylabel('Current / mA')
        
        return fig, ax1, ax2
    ax1.plot(1e3*Vcell[mask],1e6*P[mask],'.',label=label)
    ax2.plot(1e3*Vcell[mask],1e3*I[mask],'.',label=label)

def main1():
    fig,ax1,ax2 = plotAllTogether(None,None,None,None,None,None,None,None)
    for cellName,cellFilename,thermalFilename,intervals in todolist:
        figTrial,ax1Trial,ax2Trial = plotAllTogether(None,None,None,None,None,None,None,None,3)
        #figname = getFigname(cellFilename)
        #if os.path.exists(figname):
        #    continue
        
        print "Read cell data for trial: {}".format(cellFilename)
        tCell, Vcell, I, P, OCcount = fetchCellData(cellFilename)
        print "Read thermal data for trial: {}".format(thermalFilename)
        thermalData = fetchThermalData(thermalFilename)
        tThermal=thermalData['ComputerTime']

        mask = np.logical_or(OCcount == 0, OCcount > 80)
        for maskStartSt,maskStopSt in masks:
            maskStart, maskStop = fun(maskStartSt), fun(maskStopSt)
            mask = np.logical_and(mask,
                                  np.logical_or(tCell <= maskStart,
                                                tCell > maskStop))
                                         
        for setPointName,startst,stopst in intervals:
            label=cellName+','+setPointName
            figname = getFigname(startst.replace(":","="))
            if os.path.exists(figname):
               #continue
                pass
            start,stop = fun(startst), fun(stopst)
            indicesCell = np.logical_and(start <= tCell, tCell < stop)
            t2 = tCell[indicesCell].astype(datetime.datetime)
            
            indicesThermal = np.logical_and(start <= tThermal, tThermal < stop)
            t3 = tThermal[indicesThermal].astype(datetime.datetime)
            plotStuff(t2,Vcell[indicesCell],I[indicesCell],P[indicesCell],
                      mask[indicesCell],
                      t3,thermalData[indicesThermal],
                      label)
            plt.savefig(figname)
            #plt.show()
            plt.close()
            plotAllTogether(figTrial,ax1Trial,ax2Trial,Vcell[indicesCell],I[indicesCell],P[indicesCell],
                      mask[indicesCell],label)
            plotAllTogether(fig,ax1,ax2,Vcell[indicesCell],I[indicesCell],P[indicesCell],
                      mask[indicesCell],label)
            
        ax2Trial.legend(loc='upper center',bbox_to_anchor=[0.5,-0.2],
               fancybox=True, shadow=True)
        figTrial.savefig(getFigname('everything_'+cellFilename))
        plt.close()
        
    ax2.legend(loc='upper center',bbox_to_anchor=[0.5,-0.2],
               fancybox=True, shadow=True)
    ax1.set_ylim([0,300])
    ax2.set_ylim([0,25])
    plt.savefig(getFigname('everything'))
    ax1.set_ylim([0,0.5])
    ax2.set_ylim([0,0.045])
    plt.savefig(getFigname('everything_small'))
    plt.close()
        
if __name__ == "__main__":
    main1()
    
