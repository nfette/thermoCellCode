from __future__ import print_function
import pickle
from keithley6517b_alpha import calibrationType

with open('data/calibration/rs500/05ohm.pkl','r') as f:
    calibration = pickle.load(f)
    print(calibration)
