import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
imu = imudrv.Imu9IO()


x_acc, y_acc, z_acc = imu.read_accel_raw()





