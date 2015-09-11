import measure_open_circuit
import siteDefs
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates

# Pick a file, any file
where = "{}{}".format(siteDefs.data_base_dir,measure_open_circuit.subfolder)
files = os.listdir(where)
whens = []
for fname in files:
    try:
        when = measure_open_circuit.getWhenFromFilename(fname)
        whens.append(when)
    except:
        pass
whens = np.array(whens)
whens.sort()
latest = whens[-1]
print "Reading most recent open circuit voltage, started at", latest
fname = measure_open_circuit.getFilename(latest)

# Read it
def fun2(s):
    try:
        t = datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S.%f")
    except:
        t = datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S")
    return t
dtype='<M8[s],<f8,S3'
data = np.genfromtxt(fname, delimiter=",", names=True, skip_footer=3,
                     usecols=1)
dataT = np.genfromtxt(fname, delimiter=",", names=True, skip_footer=3,
                     dtype="datetime64", converters={0:fun2}, usecols=0)
Vcell = -data['Voltage']
plt.plot(dataT,1e3 * Vcell)
plt.xlabel('Time')
plt.ylabel('Cell Voltage / mV')
plt.ylim([0,50])
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.setp( plt.gca().xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right' )
plt.gcf().autofmt_xdate()
plt.gca().grid(True,axis='x')
plt.savefig(fname + '.png')
