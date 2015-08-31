import datetime
import binascii
import string
import os
import libcr23x
import siteDefs

import sys

if len(sys.argv) == 2:
    myfile = sys.argv[1]
else:
    myfile = "cr23x_outputs_2015-08-30T20=00=45.371000.dat"
    myfile = "{}{}".format(siteDefs.data_base_dir, myfile)

with open(myfile, 'r') as f:
    for line in f:
        print line

    
