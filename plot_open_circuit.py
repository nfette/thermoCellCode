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

with open(fname,'r') as f:
    line = f.readline()
names = line.strip().split(',')

dtype='<M8[s],<f8,S3'
if len(names)==3:
    data = np.genfromtxt(fname, delimiter=",", names=True, skip_footer=3,
                     usecols=1)
elif len(names)==5:
    data = np.genfromtxt(fname, delimiter=",", names=True, skip_footer=3,
                     usecols=[1,2,3,4])
elif len(names)==6:
    data = np.genfromtxt(fname, delimiter=",", names=True, skip_footer=3,
                     usecols=[1,2,3,4,5])
dataT = np.genfromtxt(fname, delimiter=",", names=True, skip_footer=3,
                     dtype="datetime64", converters={0:fun2}, usecols=0)
npoints = min(len(data),len(dataT))
Vsrc = data['Vsource']
Vread = data['Voltage']
Rsensor = data['Rsensor']
Rbypass = data['Rbypass']
Vsens = Vsrc - Vread
Vcell = -Vread
I = Vsens / Rsensor + Vcell/Rbypass
P = Vcell * I
# Not particularly useful
P_max = P.max()
I_sc = abs(I).max()

fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)
ax1.plot(dataT[max(0,npoints-2500):npoints],
         1e3 * Vcell[max(0,npoints-2500):npoints], 'b.')
ax1.set_xlabel('Time')
ax1.set_ylabel('Cell Voltage / mV')
#ax.set_ylim([-200,200])
ax1.grid(True,axis='both')

ax2.plot(dataT[max(0,npoints-2500):npoints],
         1e3 * I[max(0,npoints-2500):npoints], 'r.')
ax2.set_ylabel('Cell current / mA')
ax2.grid(True,axis='both')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.setp( ax2.xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right' )
fig.autofmt_xdate()

plt.savefig(fname + 'fig1.png')
plt.close()

if npoints > 2500:
    plt.plot(dataT[:npoints],1e3 * Vcell[:npoints], '.', ms=1)
    plt.xlabel('Time')
    plt.ylabel('Cell Voltage / mV')
    plt.ylim([-200,200])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp( plt.gca().xaxis.get_majorticklabels(), rotation=20, horizontalalignment='right' )
    plt.gcf().autofmt_xdate()
    plt.gca().grid(True,axis='both')
    plt.savefig(fname + 'fig2.png')
    plt.close()

plt.plot(1e3*I[max(0,npoints-2500):npoints],
         1e3*Vcell[max(0,npoints-2500):npoints],'.')
plt.ylabel("Voltage / mV")
plt.xlabel("Current / mA")
plt.savefig(fname + "fig3.png")
plt.close()

plt.plot(1e3*I[max(0,npoints-2500):npoints],
         1e6*P[max(0,npoints-2500):npoints],'.')
plt.xlabel("Current / mA")
plt.ylabel("Power / uW")
plt.savefig(fname + "fig4.png")
plt.close()
