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
from mpl_toolkits.mplot3d import Axes3D

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

jointypefields = ['start','stop','times','PmaxArray','E0_Array','R_Array']
jointype = namedtuple('jointype',jointypefields)
jointype2fields = ['dataT','Th','Tc','Tave','Tdelta']
jointype2 = namedtuple('jointype2',jointype2fields)

def getJoinDataFilename(start,stop):
    fmt = "%Y-%m-%dT%H=%M=%S.%f"
    startstr = start.strftime(fmt)
    stopstr = stop.strftime(fmt)
    joindatadir = siteDefs.data_base_dir + "join/"
    fname = "start{}_stop{}.pkl".format(startstr,stopstr)
    return joindatadir + fname

def getJoin2DataFilename(myfile):
    fname = myfile + ".pkl"
    joindatadir = siteDefs.data_base_dir + "join/"
    join2Filename = joindatadir + fname
    return join2Filename

if __name__ == "__main__":

    start = datetime.datetime(2015,9,5)
    stop = datetime.datetime(2015,9,7)

    windows = [(datetime.datetime(2015,9,5,17,20),datetime.datetime(2015,9,5,17,30)),
               (datetime.datetime(2015,9,5,18,30),datetime.datetime(2015,9,5,18,40)),
               (datetime.datetime(2015,9,5,20,30),datetime.datetime(2015,9,5,20,40)),
               (datetime.datetime(2015,9,5,22,20),datetime.datetime(2015,9,5,22,30))]
    colors = ['r','g','b','m']
    
    ##########################################
    # First read through all available       #
    # curve traces for desired time interval #
    ##########################################
    print "Checking if we've already read the curve trace directory ..."
    joinFilename = getJoinDataFilename(start, stop)
    try:
        # Have we already done this?
        with open(joinFilename,'r') as f:
            print "Reading curve trace info pickle from last time."
            data = pickle.load(f)
        start, stop, times, PmaxArray, E0_Array, R_Array = data
        del data
    except:
        # No we haven't ...
        print "Reading curve trace files directory ..."
        times = getCurveTraceTimes(start,stop)
        print "Found {} files. Reading through them ...".format(len(times))
        PmaxArray = []
        E0_Array = []
        R_Array = []
        for time in times:
            outputPickle, outputPlot = keithley6517b_delta.picklePlotFileNames(time)
            data, I, Vcell, Power, Pmax, fit = unpickletest2.main(outputPickle)
            PmaxArray.append(Pmax)
            E0_Array.append(fit[1])
            R_Array.append(-fit[0])
        print "Done looping through all the curve trace files."
        print "Plotting ..."
        PmaxArray = np.array(PmaxArray)
        E0_Array = np.array(E0_Array)
        R_Array = np.array(R_Array)
        joinData = jointype(start, stop, times, PmaxArray, E0_Array, R_Array)
        with open(joinFilename, 'wb') as f:
            pickle.dump(joinData,f)
        del joinData

    ##############################
    # Load the temperature data. #
    ##############################
    # For convenience, just look at one temperature data file,
    # since we know which one:
    myfile = "cr23x_outputs_2015-09-05T15=58=48.149000.dat"
    join2Filename  = getJoin2DataFilename(myfile)
    try:
        with open(join2Filename,'r') as f2:
            print "Reading temperature info pickle from last time."
            data = pickle.load(f2)
        dataT, Th, Tc, Tave, Tdelta = data
        del data
    except:    
        myfilefull = "{}{}".format(siteDefs.data_base_dir, myfile)
        print "Loading temperature data from", myfile
        dataT, Th, Tc, Tave, Tdelta = cr23x_post_process2.main(myfilefull)
        joindata2 = jointype2(dataT,Th,Tc,Tave,Tdelta)
        with open(join2Filename, 'wb') as f2:
            pickle.dump(joindata2, f2)
        del joindata2

    #############################
    # Plot what we have so far. #
    #############################

    fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)
    ax1.plot(times,1e6*PmaxArray,'^r-',markevery=50,label="$P_{max}$")
    ax1.set_title(myfile)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Max power output, $\mu$W')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    ax1.grid(True,axis='both')
    ax1b = ax1.twinx()
    ax1b.plot(dataT,Th,label="Hot electrode")
    ax1b.plot(dataT,Tc,label="Cold electrode")
    ax1b.plot(dataT,Tave,label="Average")
    ax1b.plot(dataT,Tdelta,label="Difference")
    ax1b.legend(loc='best')
    ax1b.set_ylabel('Electrode temperature, $^\circ$C')

    for window, c in zip(windows, colors):
        ax1.axvspan(window[0], window[1], color=c, alpha=0.5)

    ln1 = ax2.plot(times, E0_Array * 1e3,'db-',markevery=50,label="$E_{OC}$")
    ax2.set_ylabel("Open circuit voltage / mV")
    ax2.set_xlabel("Time")
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    ax2.grid(True,axis='both')
    ax2b = ax2.twinx()
    ln2 = ax2b.plot(times, R_Array,'sg-',markevery=50,label="R")
    ax2b.set_ylabel("Internal electrical resistance / $\Omega$")
    lns = ln1 + ln2
    labs = [l.get_label() for l in lns]
    ax2b.legend(lns, labs, loc='best')

    for window, c in zip(windows, colors):
        ax2.axvspan(window[0], window[1], color=c, alpha=0.5)
    
    plt.show()

    ################################################################
    # For each curve trace event, match up the corresponding time  #
    # interval to select temperature data.                         #
    ################################################################

    # Just for fun, let's look at the intervals between curve traces.
    tdeltas = np.diff(times)
    plt.hist(map(lambda(t):t.total_seconds(),tdeltas),
             bins=50,log=True,range=[0,100])
    plt.show()
    
    myfile = "join_temperature_2015-09-05"
    join2Filename  = getJoin2DataFilename(myfile)
    try:
        with open(join2Filename,'r') as f2:
            print "Reading join info pickle from last time."
            data = pickle.load(f2)
        iOkay, jTh, jTc, jTave, jTdelta = data
        jdataT = times[iOkay]
        del data
    except RuntimeError as e:
        print e
        print "Calculating joint temperature intervals ..."
        # Some variables for the joined data
        iOkay, jTh, jTc, jTave, jTdelta = [],[],[],[],[]

        # Let's start with just looking ahead 20 seconds
        dtmax = datetime.timedelta(seconds=20)
        for i in range(len(tdeltas)):
            t, dt = times[i], tdeltas[i]
            dt = min(dt, dtmax)
            start, stop = t, t + dt
            interval = (dataT >= start) & (dataT < stop)
            if interval.any():
                iOkay.append(i)
                jTh.append(Th[interval].mean())
                jTc.append(Tc[interval].mean())
                jTave.append(Tave[interval].mean())
                jTdelta.append(Tave[interval].mean())
                # Now what do you want to do with it?
        iOkay = np.array(iOkay)
        jTh = np.array(jTh)
        jTc = np.array(jTc)
        jTave = np.array(jTave)
        jTdelta = np.array(jTdelta)
        jdataT = times[iOkay]
        
        joindata2 = jointype2(iOkay,jTh,jTc,jTave,jTdelta)
        with open(join2Filename, 'wb') as f2:
            pickle.dump(joindata2, f2)
        del joindata2

    # Plot R and E0 against electrode temperatures
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(jTc, jTh, 1e3 * E0_Array[iOkay], c=1e3 * E0_Array[iOkay])
    ax.set_xlabel("Cold electrode temperature / $^\circ$C")
    ax.set_ylabel("Hot electrode temperature / $^\circ$C")
    ax.set_zlabel("Open circuit voltage / mV")
    #plt.colorbar()
    plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(jTc, jTh, R_Array[iOkay], c=R_Array[iOkay])
    ax.set_xlabel("Cold electrode temperature / $^\circ$C")
    ax.set_ylabel("Hot electrode temperature / $^\circ$C")
    ax.set_zlabel("Internal electrical resistance / $\Omega$")
    #plt.colorbar()
    plt.show()
    
    # Plot curve traces for selected windows
    fig = plt.figure()
    lns,labs=[],[]
    for (start, stop), color in zip(windows,colors):
        print start
        print stop
        print color
        PmaxArray = []
        for t in jdataT:
            if start <= t and t < stop:
                outputPickle, outputPlot = keithley6517b_delta.picklePlotFileNames(t)
                data, I, Vcell, Power, Pmax, fit = unpickletest2.main(outputPickle)
                PmaxArray.append(Pmax)
                l = plt.plot(1e3 * I, 1e6 * Power, '-'+color)
        PmaxArray = np.array(PmaxArray)
        lns += l
        interval = (jdataT >= start) & (jdataT < stop)
        Th_during_interval = jTh[interval].mean()
        Th_std = jTh[interval].std()
        Tc_during_interval = jTc[interval].mean()
        Tc_std = jTc[interval].std()
        Pmax_during_interval = PmaxArray.mean()
        Pmax_std = PmaxArray.std()

        fmt = "$T_h = {:0.2f} \pm {:0.2f}$, " \
              "$T_c = {:0.2f} \pm {:0.2f}$, " \
              "$P_{{max}} = {:0.2f} \pm {:0.2f}$, "\
              "$N = {}$"
        lab = fmt.format(
            Th_during_interval, Th_std,
            Tc_during_interval, Tc_std,
            1e6 * Pmax_during_interval, 1e6 * Pmax_std,
            interval.sum())
        labs += [lab]
    plt.xlabel("Cell current / mA")
    plt.ylabel("Cell power / $\mu$W")
    plt.xlim([0,10])
    plt.ylim([0,100])
    plt.legend(lns,labs,loc='best')
    plt.show()
    
