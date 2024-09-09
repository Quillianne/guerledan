# -*- coding: utf-8 -*-
import sys
import numpy as np
import time
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
imu = imudrv.Imu9IO()

# Fonction pour capturer les données magnétiques
def capturer_donnees_mag(imu, duree=5):
    """
    Capture les données magnétiques brutes pendant une durée donnée.
    Retourne la moyenne des lectures.
    """
    t0 = time.time()
    mesures = []
    
    while time.time() - t0 < duree:
        mesures.append(imu.read_mag_raw())
    
    # Moyenne des mesures
    return np.mean(mesures, axis=0)

# Fonction de calibration principale
def calibration_magnetique(beta=46, nb_mesures=4):
    """
    Effectue la calibration magnétique à partir de nb_mesures dans différentes positions.
    Retourne la matrice de calibration A et le vecteur de biais b.
    """
    donnees = np.zeros((nb_mesures, 3))
    
    # Capture des données magnétiques pour nb_mesures positions différentes
    for i in range(nb_mesures):
        input('Positionner le bateau pour la mesure {}'.format(i))
        donnees[i] = capturer_donnees_mag(imu)
        print('Mesure {}: {}'.format(i, donnees[i]))
    
    # Transposition des données
    donnees = donnees.T
    print("Données capturées:\n", donnees)
    
    # Calcul du vecteur de biais b
    b = (-donnees[:, 0] - donnees[:, 1]) / 2
    print("Vecteur de biais (b):\n", b)
    
    # Calcul de la matrice de calibration A
    x1 = donnees[:, 0] + b
    x2 = donnees[:, 2] + b
    x3 = donnees[:, 3] + b
    X = np.column_stack((x1, x2, x3))
    A = (1 / beta) * X
    print("Matrice de calibration (A):\n", A)
    
    # Sauvegarde des résultats
    np.save('A2', A)
    np.save('b2', b)
    
    return A, b

# Exécution de la calibration
A, b = calibration_magnetique()
