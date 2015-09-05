import itertools
import time

"""
This is the code for I-V curve tracing. It is fairly lazy.
"""

fileToRun = 'keithley6517b_delta.py'
try:
    for n in itertools.count():
        execfile(fileToRun)
        time.sleep(1.0)
except KeyboardInterrupt:
    pass

