import datetime
import binascii
import string
import os
import libcr23x
import siteDefs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

def main(myfile, savePlots=False):
    basename = os.path.basename(myfile)
    startdate = datetime.datetime.strptime(basename,
                                           "cr23x_outputs_%Y-%m-%dT%H=%M=%S.%f.dat")

    with open(myfile, 'r') as f:
        line1 = f.readline()
        line2 = f.readline()

    cols = len(line1.split(','))
    data = np.genfromtxt(myfile, delimiter=",",names=True, usecols=range(2,cols),
                         skip_footer=2)

    # Note that the CR23x timestamp does not include date. So attach that...
    # because otherwise, if the data run through midnight, then they are disordered.
    d = startdate.date()
    def fun2(s):
        try:
            t = datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S.%f")
        except:
            t = datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S")
        return t

    dataT = np.genfromtxt(myfile, delimiter=",",names=True,
                          usecols=[0], dtype='datetime64',skip_footer=2,
                          converters={0:fun2})

    # Some data processing
    alphaH, alphaC = 0.5, 0.5
    Th = alphaH * data['T_h_dry'] + (1. - alphaH) * data['T_h_wet']
    # Temporary fix for bad T_h_wet data
    Th = data['T_h_dry']
    Tc = alphaC * data['T_c_dry'] + (1. - alphaC) * data['T_c_wet']
    Tave = 0.5 * Th + 0.5 * Tc
    Tdelta = Th - Tc

    if savePlots:
        plt.plot(Tc, Th, 'o')
        plt.xlabel('Cold electrode, $^\circ C$')
        plt.ylabel('Hot electrode, $^\circ C$')
        plt.title(basename)
        plt.savefig(myfile + ".fig1.png")
        plt.close()

        plt.plot(Tave, Tdelta, 'o')
        plt.xlabel('Average temperature, $^\circ C$')
        plt.ylabel('Temperature difference, $^\circ C$')
        plt.title(basename)
        plt.savefig(myfile + ".fig2.png")
        plt.close()

        npoints = min(len(dataT),len(data))
        print npoints
        
        if npoints > 600:
            plt.figure(figsize=(16,8))
            #plt.xticks(rotation=20)
            for name in data.dtype.names:
                if name == "T_h_wet":
                    continue
                plt.plot(dataT[npoints-300:npoints], data[name][npoints-300:npoints], label=name)
            plt.setp( plt.gca().xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right' )
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.gcf().autofmt_xdate()
            plt.gca().grid(True,axis='x')
            plt.legend(loc='best')
            plt.xlabel('Time')
            plt.ylabel('Temperature $^\circ C$')
            plt.ylim([0,130])
            plt.title(basename)
            plt.savefig(myfile + ".fig3.png")
            plt.close()
            
        plt.figure(figsize=(16,8))
        #plt.xticks(rotation=20)
        for name in data.dtype.names:
            if name == "T_h_wet":
                    continue
            plt.plot(dataT[:npoints], data[name][:npoints], label=name)
        plt.setp( plt.gca().xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right' )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gcf().autofmt_xdate()
        plt.gca().grid(True,axis='x')
        plt.legend(loc='best')
        plt.xlabel('Time')
        plt.ylabel('Temperature $^\circ C$')
        plt.ylim([0,130])
        plt.title(basename)
        plt.savefig(myfile + ".fig4.png")
        plt.close()

        

    return dataT, Th, Tc, Tave, Tdelta

if __name__ == "__main__":
    if len(sys.argv) == 2:
        myfile = sys.argv[1]
    else:
        myfile = "cr23x_outputs_2015-09-16T13=21=06.802000.dat"
        myfile = "{}{}".format(siteDefs.data_base_dir, myfile)
    main(myfile,True)
