import itertools
import time

"""
This is the code for temperature post-processing. It is fairly lazy.
"""

fileToRun = 'cr23x-post-process2.py'
try:
    for n in itertools.count():
        execfile(fileToRun)
        time.sleep(60.0)
except KeyboardInterrupt:
    pass

