from libkeithley6517b import pvpanelType
import keithley6517b_delta
import unpickletest2
import cr23x_post_process2
import siteDefs
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import namedtuple
import pickle

def filename2timestamp(myfile):
    try:
        time = datetime.datetime.strptime(myfile, "%Y-%m-%dT%H=%M=%S.%f.pkl")
    except:
        try:
            time = datetime.datetime.strptime(myfile, "%Y-%m-%dT%H=%M=%S.pkl")
            print "spot on there"
        except:
            time = None
            #print myfile
    finally:
        return time

def getCurveTraceTimes(start,stop):
    mydir = siteDefs.data_base_dir + "curve_traces/"
    files=os.listdir(mydir)
    #times = map(filename2timestamp,files)
    times = []
    for afile in files:
        time = filename2timestamp(afile)
        if time and start < time and time < stop:
            times.append(time)
    times = np.array(times)
    return times

jointypefields = ['start','stop','times','PmaxArray']
jointype = namedtuple('jointype',jointypefields)

def getJoinDataFilename(start,stop):
    fmt = "%Y-%m-%dT%H=%M=%S.%f"
    startstr = start.strftime(fmt)
    stopstr = stop.strftime(fmt)
    joindatadir = siteDefs.data_base_dir + "join/"
    fname = "start{}_stop{}.pkl".format(startstr,stopstr)
    return joindatadir + fname

if __name__ == "__main__":
    start = datetime.datetime(2015,9,5)
    stop = datetime.datetime(2015,9,7)
    
    # First read through all available curve traces for desired time interval
    print "Checking if we've already read the curve trace directory ..."
    joinFilename = getJoinDataFilename(start, stop)
    try:
        with open(joinFilename,'r') as f:
            data = pickle.load(f)
            start, stop, times, PmaxArray = data
    except:
        print "Reading curve trace files directory ..."
        times = getCurveTraceTimes(start,stop)
        print "Found {} files. Reading through them ...".format(len(times))
        PmaxArray = []
        for time in times:
            outputPickle, outputPlot = keithley6517b_delta.picklePlotFileNames(time)
            data, I, Vcell, Power, Pmax, fit = unpickletest2.main(outputPickle)
            PmaxArray.append(Pmax)
        print "Done looping through all the curve trace files."
        print "Plotting ..."
        PmaxArray = np.array(PmaxArray)
        joinData = jointype(start, stop, times, PmaxArray)
        with open(joinFilename, 'wb') as f:
            pickle.dump(joinData,f)

    fig, ax1 = plt.subplots()
    ax1.plot(times,1e6*PmaxArray,'r.')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Max power output, $\mu$W')
    plt.setp( ax1.xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right' )
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    ax1.grid(True,axis='x')

    # Load the temperature data.
    # For convenience, just look at one temperature data file,
    # since we know which one:
    myfile = "cr23x_outputs_2015-09-05T15=58=48.149000.dat"
    myfile = "{}{}".format(siteDefs.data_base_dir, myfile)
    print "Loading temperature data from", myfile
    dataT, Th, Tc, Tave, Tdelta = cr23x_post_process2.main(myfile)

    ax2 = ax1.twinx()
    ax2.plot(dataT,Th,label="Hot electrode")
    ax2.plot(dataT,Tc,label="Cold electrode")
    ax2.plot(dataT,Tave,label="Average")
    ax2.plot(dataT,Tdelta,label="Difference")
    ax2.legend(loc='best')
    ax2.set_ylabel('Electrode temperature, $^\circ$C')
    
    plt.show()

    
