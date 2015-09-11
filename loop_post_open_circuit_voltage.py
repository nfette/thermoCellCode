import datetime
import itertools
import time

"""
This is the code for open-circuit voltage post-processing. It is fairly lazy.
"""

fileToRun = 'plot_open_circuit.py'
timeToWait = 30
a = range(timeToWait)
a.reverse()
for n in itertools.count():
    try:
        t = datetime.datetime.now()
        print "[{}] Start crunching numbers ...".format(t.isoformat()),
        execfile(fileToRun)
        print " plots updated."
        print "sleeping",
        for i in a:
            print '\b'*80,
            print 'sleeping {} seconds'.format(i),
            time.sleep(1)
        print '\b'*80,
    except KeyboardInterrupt:
        break

