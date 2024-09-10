import numpy as np
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))
import arduino_driver_v2 as arddrv

ard = arddrv.ArduinoIO()
spdleft = 0
spdright = 0
ard.send_arduino_cmd_motor(spdleft, spdright)