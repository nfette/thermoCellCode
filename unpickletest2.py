# -*- coding: utf-8 -*-

from __future__ import print_function
import pickle
from libkeithley6517b import pvpanelType
import siteDefs
import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys
import inset_subplot

#TODO: make this a command line argument

def main(myfile,savePlots=False,verbose=False):
    if verbose:
        print("Opening {} ...".format(myfile))
    with open(myfile,'r') as f:
        data = pickle.load(f)
    #print(data)
    npoints = 1+(data.stop-data.start)/data.step
    Vin = np.linspace(data.start,data.stop,npoints)
    Vout, time, iSample = data.data.T
    Vcell = -Vout
    V_current_sensor = Vin - Vout
    I = V_current_sensor / data.r_current_sensor
    # If the current went beyond 10 mA, chop off those values
    badIndices = I > 10e-3
    I = I[-badIndices]
    Vcell = Vcell[-badIndices]
    Power = Vcell * I
    Pmax = Power.max()

    # Linear fit the data
    fit = np.polyfit(I, Vcell, 1)

    if savePlots:
        datestr = data.date.isoformat().replace(":","=")
        fig1 = siteDefs.data_base_dir + "power_vs_current/" + datestr + "_figure1.png"
        fig2 = siteDefs.data_base_dir + "power_vs_current/" + datestr + "_figure2.png"

        fig=plt.figure(1,figsize=(20,8))
        ax=fig.add_subplot(121)
        ax.cla()
        ax.plot(1e3 * I, 1e3 * Vcell,'o')
        ax.set_xlabel('Cell current / mA')
        ax.set_ylabel('Cell potential / mV')
        #ax.set_xlim([-0.0,12])
        #ax.set_ylim([-0.0,50])
        ax.set_xlim([-0.0,1.2])
        ax.set_ylim([-0.0,50])
        ax.set_title(data.date.isoformat())
        rect = [0.68,0.68,0.3,0.3]
        ax2 = inset_subplot.add_subplot_axes(ax,rect)
        ax2.plot(1e3*I,1e3*Vcell)
        
        ax=fig.add_subplot(122)
        ax.cla()
        ax.plot(1e3 * I, 1e6 * Power,'o')
        ax.set_xlim([0.0,1.2])
        ax.set_ylim([0,20])
        ax.set_xlabel('Cell current / mA')
        ax.set_ylabel('Power generated / $\mu$W')
        ax.set_title(data.date.isoformat())
        rect=[0.68,0.68,0.3,0.3]
        #ax2=inset_subplot.add_subplot_axes(ax,rect)
        #ax2.plot(1e3*I, 1e6*Power)
        plt.savefig(fig1)

        #plt.show()
        plt.close('all')
        
    return data, I, Vcell, Power, Pmax, fit

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read the argument
        for myfile in sys.argv[1:]:
            main(myfile,True,True)
    else:
        # Probably we can do the example
        print("Usage: python unpickletest2.py SomeIVfileData.pkl")
        print("Warning: No file given! I'll run default as example...")
        myfile = siteDefs.data_base_dir + "curve_traces/" + "2015-09-11T02=19=11.372000.pkl"
        data, I, Vcell, Power, Pmax, fit = main(myfile,True,True)
