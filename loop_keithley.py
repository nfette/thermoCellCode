import itertools
import time

fileToRun = 'keithley6517b_delta.py'
try:
    for n in itertools.count():
        execfile(fileToRun)
        time.sleep(10.0)
except KeyboardInterrupt:
    pass

