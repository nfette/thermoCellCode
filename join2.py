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
        
todolist = ['2015-09-13T18=38=23.924000.dat',
            '2015-09-10T21=46=34.891000.dat',
            "2015-09-21T20=30=53.154000.dat",
            "2015-09-23T09=46=55.059000.dat",
            "2015-09-24T11=13=51.022000.dat"]

def getNames(fname):
    uniformName = "{}{}{}".format(
        siteDefs.data_base_dir,"uniform_data/",fname)
    uniformPickle = "{}{}{}".format(
        siteDefs.data_base_dir,"uniform_data/",os.path.splitext(fname)[0] + '.pkl')
    return uniformName, uniformPickle

def getFigname(fname):
    figname = "{}{}{}".format(
        siteDefs.data_base_dir,"uniform_data/",os.path.splitext(fname)[0] + '.fig1.png')
    return figname

def fetch(fname):
    # Read the data
    uniformName, uniformPickle = getNames(fname)
    
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
        Vsens = Vsens = Vsrc - Vread
        I = Vsens / Rsensor + Vcell/Rbypass
        P = Vcell * I
        with open(uniformPickle,'wb') as f:
            pickle.dump(join2types.uDataType(t,Vcell,I,P),f)
    return t, Vcell, I, P

if __name__ == "__main__":
    for fname in todolist:
        figname = getFigname(fname)
        if os.path.exists(figname):
            continue
        
        print "Read data for trial: {}".format(fname)
        t, Vcell, I, P = fetch(fname)
        t2 = t.astype(datetime.datetime)
        del t
        fig, (ax1, ax2, ax3) = plt.subplots(3,1,sharex=True,figsize=(300,10))
        ax1.plot(t2,Vcell)
        ax1.set_ylabel('Voltage')
        ax1.set_yscale('symlog',linthreshy=1e-2)
        ax1.grid(True,which='both',axis='both')
        ax2.plot(t2,I)
        ax2.set_ylabel('Current')
        ax2.set_yscale('symlog',linthreshy=1e-2)
        ax2.grid(True,which='both',axis='both')
        ax3.plot(t2,P)
        ax3.set_ylabel('Power')
        ax3.set_yscale('symlog',linthreshy=1e-4)
        ax3.grid(True,which='both',axis='both')
        ax3.xaxis.set_major_locator(mdates.HourLocator(tz=tz))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=tz))
        ml=mdates.MinuteLocator(byminute=[0,20,40],tz=tz)
        ml.MAXTICKS = 4000
        ax3.xaxis.set_minor_locator(ml)
        plt.setp( ax3.xaxis.get_majorticklabels(), rotation=20,
              horizontalalignment='right' )
        fig.autofmt_xdate()
        plt.savefig(fname+'_fig1.png')
        plt.close()
        
