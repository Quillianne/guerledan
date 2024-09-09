# -*- coding: utf-8 -*-
import sys
import numpy as np
from time import time
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
imu = imudrv.Imu9IO()


# récupération des données de calibration
A = np.load('A100.npy')
b = np.load('b100.npy')

# mesure des accélérations pour vérifier (typiquement bateau à plat pour obtenir g=9.81)
t0 = time.time()
mesures = []
while time.time() - t0 < 5:
    mesures.append(imu.read_acc_raw())
# Moyenne des mesures et vecteur X
X = np.mean(mesures, axis=0).T

# obtention des accélérations corrigées
Y = np.linalg.inv(A)@(X + b)

# affichage
print(Y)
