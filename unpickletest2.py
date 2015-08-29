from __future__ import print_function
import pickle
from keithley6517b_gamma import pvpanelType
import siteDefs
import numpy as np
import matplotlib.pyplot as plt
import datetime

#TODO: make this a command line argument
myfile = siteDefs.data_base_dir + "curve_traces/" + "2015-08-28T18=45=31.788000.pkl"


with open(myfile,'r') as f:
    data = pickle.load(f)
    print(data)
    npoints = 1+(data.stop-data.start)/data.step
    Vin = np.linspace(data.start,data.stop,npoints)
    Vout, time, iSample = data.data.T
    V_current_sensor = Vin - Vout
    I = V_current_sensor / data.r_current_sensor
    Power = -Vout * I

    datestr = data.date.isoformat().replace(":","=")
    fig1 = siteDefs.data_base_dir + "power_vs_current/" + datestr + "_figure1.png"
    fig2 = siteDefs.data_base_dir + "power_vs_current/" + datestr + "_figure2.png"
    
    plt.figure(1)
    plt.cla()
    plt.plot(I,Power)
    plt.xlabel('current / Amps')
    plt.ylabel('voltage / Watts')
    plt.savefig(fig1)

    plt.figure(2)
    plt.cla()
    plt.plot(I,Power)
    plt.xlim([0,0.0015])
    plt.ylim([0,max(Power)])
    plt.xlabel('current / Amps')
    plt.ylabel('voltage / Watts')
    plt.savefig(fig2)

    #plt.show()
    plt.close('all')
