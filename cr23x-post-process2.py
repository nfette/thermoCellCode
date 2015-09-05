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

if len(sys.argv) == 2:
    myfile = sys.argv[1]
else:
    myfile = "cr23x_outputs_2015-09-05T15=58=48.149000.dat"
    myfile = "{}{}".format(siteDefs.data_base_dir, myfile)

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
    t = datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S.%f")
    return t

dataT = np.genfromtxt(myfile, delimiter=",",names=True,
                      usecols=[0], dtype='datetime64',skip_footer=2,
                      converters={0:fun2})

# Some data processing
Th = 0.5 * data['T_h_dry'] + 0.5 * data['T_h_wet']
Tc = 0.5 * data['T_c_dry'] + 0.5 * data['T_c_wet']
plt.plot(Tc, Th, 'o')
plt.xlabel('Cold electrode, $^\circ C$')
plt.ylabel('Hot electrode, $^\circ C$')
plt.title(basename)
plt.savefig(myfile + ".fig1.png")
plt.close()

Tave = 0.5 * Th + 0.5 * Tc
Tdelta = Th - Tc
plt.plot(Tave, Tdelta, 'o')
plt.xlabel('Average temperature, $^\circ C$')
plt.ylabel('Temperature difference, $^\circ C$')
plt.title(basename)
plt.savefig(myfile + ".fig2.png")
plt.close()

plt.figure(figsize=(16,8))
#plt.xticks(rotation=20)
for name in data.dtype.names:    
    plt.plot(dataT, data[name], label=name)
plt.setp( plt.gca().xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right' )
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.gcf().autofmt_xdate()
plt.gca().grid(True,axis='x')
plt.legend(loc='best')
plt.xlabel('Time')
plt.ylabel('Temperature $^\circ C$')
plt.ylim([0,130])
plt.title(basename)
plt.savefig(myfile + ".fig3.png")
plt.close()
