import itertools
import time
import measure_open_circuit
import sys

"""
This is the code for I-V curve tracing. It is fairly lazy.
"""

fileToRun = 'keithley6517b_delta.py'

if len(sys.argv) == 2:
    filename = sys.argv[1]
    headers = False
else:
    when = datetime.datetime.now()
    filename = measure_open_circuit.getFilename(when)
    headers = True
print(filename)
    
try:
    with open(filename,'a') as f:
        for i in itertools.count():
            measure_open_circuit.main(f,headers,1000)

            for i in range(5):
                try:
                    time.sleep(5)
                    execfile(fileToRun)
                    time.sleep(5)
                    break
                except KeyboardInterrupt:
                    raise
                except:
                    continue
            
except KeyboardInterrupt:
    # This is not necessary, just makes for quieter quit
    pass

