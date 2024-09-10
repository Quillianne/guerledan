# -*- coding: utf-8 -*-
import sys
import numpy as np
import time
import os
from time import sleep  # Ajout de l'import pour sleep

# Ajout du chemin vers le répertoire contenant les drivers
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
imu = imudrv.Imu9IO()

# Chargement des matrices de calibration
A = np.load("A.npy")
b = np.load("b.npy")

def get_cap():
    """
    Fonction qui lit les données magnétiques, les corrige avec la matrice de calibration A et le vecteur b,
    et retourne l'angle de cap (en radians).
    """
    # Lecture des données magnétiques brutes
    x = np.array(imu.read_mag_raw())
    x = x.reshape((3, 1))  # Reshape pour un vecteur colonne
    
    sleep(1)  # Pause d'une seconde
    
    # Application de la matrice de calibration pour corriger les données
    y = np.linalg.inv(A) @ (x + b.reshape(3, 1))
    
    sleep(1)  # Pause d'une seconde
    
    # Calcul de l'angle de cap en radians (avec arctan2 pour une meilleure gestion des quadrants)
    return np.arctan2(y[1, 0], y[0, 0])

if __name__ == '__main__' :
    while True:
        # Calcul et affichage de l'angle en degrés
        theta = get_cap()
        print(theta * 180 / np.pi, "degrés")
