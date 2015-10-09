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

==To do==
* Use input files to control post-processing
* Save abbreviated data files for selected windows

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
# 2015-09-11T21:20:33.491000: bypass insert 1/2 ohm nominal
# 2015-09-11T21:22:28.863000: bypass insert 1/3 ohm nominal
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
import json
import sys

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

dtype4=[('Voltage','<f8'),
        ('Vstd','<f8'),
        ('Rsensor','<f8'),
        ('Rbypass','<f8'),
        ('Vsource','<f8'),
        ('Npoints','<i4'),
        ]

todolist = [('CuSO$_4$, plain surface, trial 1',
             '2015-09-10T21=46=34.891000.dat','cr23x_outputs_2015-09-10T21=34=56.579000.dat',
               [('setpoint A','2015-09-11T02:10:00.000000','2015-09-11T03:20:00.000000'),
                ('setpoint B','2015-09-11T13:40:00.000000','2015-09-11T14:20:00.000000'),
                ('setpoint C','2015-09-11T19:30:00.000000','2015-09-11T21:25:00.000000'),
                ('setpoint D','2015-09-12T13:00:00.000000','2015-09-12T13:32:00.000000')]),
            ('CuSO$_4$, plain surface, trial 2',
             '2015-09-13T18=38=23.924000.dat','cr23x_outputs_2015-09-13T19=49=03.865000.dat',
               [('setpoint C1','2015-09-14T13:00:00.000000','2015-09-14T14:26:00.000000'),
                ('setpoint A','2015-09-14T20:00:00.000000','2015-09-14T21:50:00.000000'),
                ('setpoint C2','2015-09-15T10:20:00.000000','2015-09-15T12:10:00.000000'),
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
                ('setpoint C1','2015-09-23T20:30:00.000000','2015-09-23T21:30:00.000000'),
                ('setpoint C2','2015-09-24T00:30:00.000000','2015-09-24T01:30:00.000000')]),
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
         ('2015-09-11T21:21:30.082000','2015-09-11T21:22:28.863000'),
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

# Read the data
def fetchCellData2(bigFilename,littleFilename,start,stop):
    try:
        print "Trying the abridged file..."
        uData = np.genfromtxt(littleFilename, delimiter=",", names=True,
                     dtype=dtype2)
        print "Read the abridged file."
    except:        
        print "Reading the full source file. This may take a little while."
        uniformName, _ = getCellDataNames(bigFilename)
        uData = np.genfromtxt(uniformName, delimiter=",", names=True,
                     dtype=dtype2)
        # Filter by time
        t=uData['ComputerTime']
        keep = np.logical_and(start <= t, t < stop)
        uData = uData[keep]
        writeArray(littleFilename,uData)
    return uData
        
def calculate(uData):
    Vsrc = uData['Vsource']
    Vread = uData['Voltage']
    Rsensor = uData['Rsensor']
    Rbypass = uData['Rbypass']
    Vcell = -Vread
    Vsens = Vsrc - Vread
    I = Vsens / Rsensor + Vcell/Rbypass
    P = Vcell * I
    return Vcell, I, P

def fetchThermalData(fname):
    thermalFileName = getThermalDataName(fname)
    # Read the data
    thermalData = np.genfromtxt(thermalFileName,delimiter=",", names=True,
                                dtype=dtype3, usecols=usecols3)
    return thermalData

def plotStuff(t,Vcell,I,P,mask,thermalData,indicesThermal,label):
    fig, (row1, row2) = plt.subplots(2,2,sharex='col',figsize=(16,8))
    ax0,ax1 = row1
    ax2,ax3 = row2
    fig.suptitle(label)

    t3 = thermalData['ComputerTime'].astype(datetime.datetime)
    for aName,aType in dtype3[1:]:
        ax0.plot(t3[indicesThermal],
                 thermalData[aName][indicesThermal],'.',label=aName)
        ax0.plot(t3[-indicesThermal],
                 thermalData[aName][-indicesThermal],'.',ms=1)
    #ax0.legend()
    ax0.set_ylim([0,120])
    ax0.set_ylabel('Temperature [$^\circ$C]')
    ax0.grid(True,which='both',axis='both')

    ax1.plot(1e3*Vcell[mask],1e6*P[mask],'o')
    ax1.set_ylabel('Power / $\mu$W')
    ax1.set_xlabel('Voltage / mV')
    ax1.grid(True,which='both',axis='both')

    ax2.plot(t[mask],1e3*Vcell[mask],'r.',label="Voltage / mV")
    ax2.plot(t[-mask],1e3*Vcell[-mask],'r.',ms=1)
    #ax2.set_ylim([-20,200])
    ax2b = ax2.twinx()
    #ax2c = ax2.twinx()
    ax2b.plot(t[mask],1e3*I[mask],'g.',label="Current / mA")
    ax2b.plot(t[-mask],1e3*I[-mask],'g.',ms=1)
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

def writeArray(fname,array):
    with open(fname,'w') as f:
        f.write("{}\n".format(','.join(array.dtype.names)))
        for row in array:
            f.write("{}\n".format(','.join([el.__str__() for el in row])))

def meanTemperature(t,n=3):
    within = np.ones_like(t,dtype='bool')
    for i in range(n):
        tguess = t.mean()
        tstd = t.std()
        within = (tguess - 2*tstd < t) * (t < tguess + 2*tstd)
        t=t[within]
    return tguess

# Filters and plots data from a specified trial
def main1(config,configdir):
    global gfig,gax1,gax2
    cellName = config["Title"]
    cellFilename = config["cellFilename"]
    thermalFilename = config["thermalFilename"]
    intervals = config["intervals"]

    # Open plots for all trial data
    figTrial,ax1Trial,ax2Trial = plotAllTogether(None,None,None,None,None,None,None,None,3)
    figTrialS,ax1TrialS,ax2TrialS = plotAllTogether(None,None,None,None,None,None,None,None,3)
    #figname = getFigname(cellFilename)
    #if os.path.exists(figname):
    #    continue
    
    print "Read thermal data for trial: {}".format(thermalFilename)
    thermalData = fetchThermalData(thermalFilename)
    for i in thermalData.dtype.names:
        try:
            #thermalData[i][thermalData[i] < 0] = np.nan
            print "<{}> = {}".format(i, thermalData[i].mean())
        except:
            pass
    tThermal=thermalData['ComputerTime']
    print "Read cell data for trial: {}".format(cellFilename)
    #tCell, Vcell, I, P, OCcount = fetchCellData(cellFilename)
                                     
    for setpoint in intervals:
        setPointName = setpoint["setPointName"]
        startst = setpoint["startst"]
        stopst = setpoint["stopst"]
        waitSecsAfterChange = setpoint["waitSecsAfterChange"]
        label=cellName+', '+setPointName
        figname = os.path.join(configdir,setPointName+".pdf")
        start,stop = fun(startst), fun(stopst)
        intervalFilename = os.path.join(configdir,setPointName+".dat")
        print "Read cell data for setpoint: {}".format(setPointName)
        
        uData = fetchCellData2(cellFilename,intervalFilename,start,stop)
        tCell = uData['ComputerTime']
        OCcount = uData['OCcount']
        Vcell, I, P,  = calculate(uData)
        t2 = tCell.astype(datetime.datetime)

        # Create masks for thermal data where curve trace is active.
        i = 0
        thermalMasks = []
        for i in range(len(uData)):
            if 'thermalMaskStart' not in locals():
                if uData[i]['OCcount'] > 0:
                    thermalMaskStart = uData[i]['ComputerTime']
            else:
                if uData[i]['OCcount'] == 0:
                    thermalMaskStop = uData[i-1]['ComputerTime']
                    thermalMasks.append((thermalMaskStart,thermalMaskStop))
                    del thermalMaskStart
        indicesThermal = np.logical_and(start <= tThermal, tThermal < stop)
        indicesThermalGood = np.zeros_like(tThermal,dtype='bool')
        for thermalMaskStart,thermalMaskStop in thermalMasks:
            indicesThermalGood += ((tThermal >= thermalMaskStart ) + (thermalMaskStop <= tThermal))
            
        # What now?
        writeArray(os.path.join(configdir,setPointName+"_thermal.txt"),
                   thermalData[indicesThermal])
        thermalMeans = np.zeros(1,dtype=dtype3)
        for i in thermalData.dtype.names:
            try:
                #thermalMeans[i] = thermalData[i][indicesThermal*indicesThermalGood].mean()
                thermalMeans[i] = meanTemperature(thermalData[i][indicesThermal*indicesThermalGood])
                print "<{}> = {}".format(i, thermalMeans[i])
                
            except:
                pass
        writeArray(os.path.join(configdir,setPointName+"_thermalmeans.txt"),thermalMeans)

        # Wearing a mask.
        mask = uData["Vsource"] >= 0
        mask *= (OCcount == 0) + (OCcount > setpoint["waitSecsAfterChange"])
        for maskStartSt,maskStopSt in config["masks"]:
            maskStart, maskStop = fun(maskStartSt), fun(maskStopSt)
            mask *= (tCell <= maskStart) + (tCell > maskStop)
        
        print "Plotting all the data."
        plotStuff(t2,Vcell,I,P,mask,
                  thermalData[indicesThermal],indicesThermalGood[indicesThermal],
                  label)
        plt.savefig(figname)
        #plt.show()
        plt.close()
        plotAllTogether(figTrial,ax1Trial,ax2Trial,Vcell,I,P,mask,label)
        plotAllTogether(gfig,gax1,gax2,Vcell,I,P,mask,label)

        # Method #1 of data simplification:
        # Sort data in order to calculate mean and std curves.
        # There are three parameters that must match to lump data together.
        # These can be expressed as a single tuple:
        # (Rbypass, Rsensor, Vsource)
        # For each lumped set, we will then ask for a mean and std of
        # Voltage(measured).
        # Note that current = function(Rbypass, Rsensor, Vsource, Voltage).
        # Therefore we can plot current(Rbypass,Rsensor,Vsource,<Voltage>) vs <Voltage>.
        # as well as
        # current(Rbypass,Rsensor,Vsource,<Voltage>+sigma(Voltage)) vs
        # <Voltage>+sigma(Voltage)
        # Note that we have to sort also <Voltage> and <V> +/- sigma(Voltage).
        # Do the same for power.
        # Additional calculation can propagate uncertainty of Rbypass, Rsensor, Vsource, etc.
        print "Applying method 1 to calculate a 'mean' set of points."
        sortBox = dict()
        for row in uData[mask]:
            tup = (row['Rbypass'],row['Rsensor'],row['Vsource'])
            if not tup in sortBox:
                sortBox[tup]=[]
            sortBox[tup].append(row['Voltage'])
        bigN = len(sortBox)
        sortstuff = np.zeros(bigN,dtype=dtype4)
        for (i,tup) in zip(range(bigN),sortBox):
            voltages=np.array(sortBox[tup])
            sortstuff[i]['Rbypass'],sortstuff[i]['Rsensor'],sortstuff[i]['Vsource']=tup
            sortstuff[i]['Voltage']=voltages.mean()
            sortstuff[i]['Vstd']=voltages.std()
            sortstuff[i]['Npoints']=voltages.size
        sortstuff.sort()
        writeArray(os.path.join(configdir,setPointName+"_stats.txt"),sortstuff)
        Vcell, I, P  = calculate(sortstuff)
        print "Plotting the 'mean' set of  points."
        plotAllTogether(figTrialS,ax1TrialS,ax2TrialS,Vcell,I,P,I>=0,label)

        # Method #2.
        # Curve fit the entire data set.
        # Assume current = function(Rbypass, Rsensor, Vsource, Voltage).
        # Choose a model for fitting, current = function(Voltage,params).
        # As above, then for an arbitrary set V, plot current(V,<params>) vs V.
        # For uncertainty, you must have a stationary correlation matrix R for params.
        # Then do some magic to compute upper and lower percentiles for {current(V,p)},
        # where p is a random variable distributed with mean <params> and correlation R.
        

    # After loop, save plots and tidy up.
    ax2Trial.legend(loc='upper center',bbox_to_anchor=[0.5,-0.2],
           fancybox=True, shadow=True)
    figTrial.savefig(os.path.join(configdir,"everything"+".pdf"))
    
    ax1TrialS.set_xlim(config["vlim"])
    ax1TrialS.set_ylim(config["plim"])
    ax2TrialS.set_xlim(config["vlim"])
    ax2TrialS.set_ylim(config["ilim"])
    ax2TrialS.legend(loc='upper center',bbox_to_anchor=[0.5,-0.2],
           fancybox=True, shadow=True)
    figTrialS.savefig(os.path.join(configdir,"statistics"+".pdf"))
    plt.close()
    return sortBox,sortstuff
        
if __name__ == "__main__":
    try:
        configFilename=sys.argv[1]
    except:
        configFilename=siteDefs.data_base_dir+"uniform_data/2015-09-24T11=13=51.022000/config.json"
    with open(configFilename,'r') as f:
        config = json.load(f)
    configdir = os.path.split(configFilename)[0]
        
    gfig,gax1,gax2 = plotAllTogether(None,None,None,None,None,None,None,None)

    sortBox,sortstuff=main1(config,configdir)
    
##    gax2.legend(loc='upper center',bbox_to_anchor=[0.5,-0.2],
##               fancybox=True, shadow=True)
##    gax1.set_ylim([0,300])
##    gax2.set_ylim([0,25])
##    plt.savefig(getFigname('everything'))
##    gax1.set_ylim([0,0.5])
##    gax2.set_ylim([0,0.045])
##    plt.savefig(getFigname('everything_small'))
##    plt.close()
