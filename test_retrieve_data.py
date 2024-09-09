import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
imu = imudrv.Imu9IO()

def print_data(sensor):
    print("MAG: " + str(sensor.read_mag_raw()))
    print("ACC: " + str(sensor.read_accel_raw()))
    print("GYRO: " + str(sensor.read_gyro_raw()))

while True:
    os.system("clear")
    print_data(imu)
    time.sleep(0.1)
