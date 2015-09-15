from __future__ import print_function
import itertools
import time
import measure_open_circuit
import libkeithley6517b
import keithley6517b_delta
import sys
import datetime

"""
This is the code for I-V curve tracing and open circuit voltage measurement.
It is fairly lazy.
"""

# Check if the user wants to append to an existing data file,
# else create a new one.
if len(sys.argv) == 2:
    filename = sys.argv[1]
    headers = False
else:
    when = datetime.datetime.now()
    filename = measure_open_circuit.getFilename(when)
    headers = True
print(filename)
    
try:
    for i in itertools.count():
        device = libkeithley6517b.getDevice()
        keithley6517b_delta.main2(device)
        with open(filename,'a') as f:
            measure_open_circuit.main(f,headers,500,device)            
except KeyboardInterrupt:
    # This is not necessary, just makes for quieter quit
    print("Closing file:",filename)
