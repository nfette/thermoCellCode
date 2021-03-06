import datetime
import itertools
import time

"""
This is the code for temperature post-processing. It is fairly lazy.
"""

fileToRun = 'cr23x_post_process2.py'
timeToWait = 15*60
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

