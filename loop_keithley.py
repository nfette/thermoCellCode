import itertools
import time

fileToRun = 'keithley6517b_gamma.py'
try:
    for n in itertools.count():
        execfile(fileToRun)
        time.sleep(10.0)
except KeyboardInterrupt:
    pass

