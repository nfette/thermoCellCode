# -*- coding: utf-8 -*-

from __future__ import print_function
import pickle
from keithley6517b_gamma import pvpanelType
import siteDefs
import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys

#TODO: make this a command line argument

def main(myfile):
    with open(myfile,'r') as f:
        data = pickle.load(f)
        print(data)
        npoints = 1+(data.stop-data.start)/data.step
        Vin = np.linspace(data.start,data.stop,npoints)
        Vout, time, iSample = data.data.T
        Vcell = -Vout
        V_current_sensor = Vin - Vout
        I = V_current_sensor / data.r_current_sensor
        Power = Vcell * I

        datestr = data.date.isoformat().replace(":","=")
        fig1 = siteDefs.data_base_dir + "power_vs_current/" + datestr + "_figure1.png"
        fig2 = siteDefs.data_base_dir + "power_vs_current/" + datestr + "_figure2.png"

        plt.figure(1,figsize=(20,8))
        plt.subplot(121)
        plt.cla()
        plt.plot(1e3 * I, 1e3 * Vcell,'o-')
        plt.xlabel('Cell current / mA)')
        plt.ylabel('Cell potential / mV')
        plt.xlim([-0.0,6])
        plt.ylim([-0.0,20])
        plt.title(data.date.isoformat())
        #plt.savefig(fig1)
        
##        plt.figure(1)
##        plt.cla()
##        plt.plot(1e3 * I, 1e6 * Power, 'o-')
##        plt.xlabel('Current / mA')
##        plt.ylabel(r'Power / $\mathrm{\mu}$W')
##        plt.savefig(fig1)

        #plt.figure(2)
        plt.subplot(122)
        plt.cla()
        plt.plot(1e3 * I, 1e6 * Power,'o-')
        #plt.xlim([0,1.1*max(1e3 * I[Power>0])])
        #plt.ylim([0,1.1*max(1e6 * Power)])
        plt.xlim([0.0,6])
        plt.ylim([0,25])
        plt.xlabel('Cell current / mA')
        plt.ylabel('Power generated / $\mu$W')
        plt.title(data.date.isoformat())
        plt.savefig(fig1)

        #plt.show()
        plt.close('all')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read the argument
        for myfile in sys.argv[1:]:
            main(myfile)
    else:
        # Probably we can do the example
        print("Usage: python unpickletest2.py SomeIVfileData.pkl")
        print("Warning: No file given! I'll run default as example...")
        myfile = siteDefs.data_base_dir + "curve_traces/" + "2015-08-28T19=43=17.673000.pkl"
        main(myfile)
