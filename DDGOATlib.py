# -*- coding: utf-8 -*-
import sys
import numpy as np
import time
import os
from time import sleep

# Ajout du chemin vers le répertoire contenant les drivers
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
import arduino_driver_v2 as arddrv

# Initialisation des capteurs et moteurs
imu = imudrv.Imu9IO()
ard = arddrv.ArduinoIO()

A = np.load("A.npy")
b = np.load("b.npy")

def get_acc_mean(imu=imu, duree=0.5):
    """
    Fonction pour capturer les données magnétiques pendant une durée (en secondes) 
    et renvoyer la moyenne des mesures sur cette période.
    """
    start_time = time.time()
    mesures = []

    # Capturer les données pendant 'duree' secondes
    while time.time() - start_time < duree:
        mesures.append(imu.read_accel_raw())

    # Calculer la moyenne des mesures
    moyenne = np.mean(mesures, axis=0)
    return np.array(moyenne)


def declenchement(imu=imu, ard=ard):
    acc_z = get_acc_mean(imu)[2]
    #print(acc_z)
    while acc_z > 2800:
        ard.send_arduino_cmd_motor(0, 0)
        acc_z = get_acc_mean(imu)[2]
        #print(acc_z)

    while acc_z < 3500:
        ard.send_arduino_cmd_motor(100, 100)
        acc_z = get_acc_mean(imu)[2]
        #print(acc_z)

def get_cap(imu=imu):
    """
    Fonction qui lit les données magnétiques, les corrige avec la matrice de calibration A et le vecteur b,
    et retourne l'angle de cap en radians.
    """
    # Lecture des données magnétiques brutes
    x = np.array(imu.read_mag_raw())
    x = x.reshape((3, 1))  # Reshape pour un vecteur colonne
    
    # Application de la matrice de calibration pour corriger les données
    y = np.linalg.inv(A) @ (x + b.reshape(3, 1))
    
    # Calcul de l'angle de cap en radians (avec arctan2 pour une meilleure gestion des quadrants)
    return np.arctan2(y[1, 0], y[0, 0])

def suivi_cap(cap_consigne, duree=60, Kp=2, spd_base=200):
    """
    Suivi du cap en fonction d'un cap de consigne (en degré) pendant une durée donnée (en secondes).
    """

    start_time = time.time()
    print("Suivi du cap de consigne: {}° pendant 1 minute...".format(cap_consigne))

    while time.time() - start_time < duree:
        # Calcul du cap actuel en radians
        cap_actuel_rad = get_cap()

        # Conversion du cap en degrés
        cap_actuel = cap_actuel_rad * 180 / np.pi

        # Calcul de l'erreur de cap
        erreur = cap_consigne - cap_actuel

        # Ajustement de l'erreur pour la circularité (entre -180 et 180 degrés)
        if erreur > 180:
            erreur -= 360
        elif erreur < -180:
            erreur += 360

        # Correction proportionnelle
        correction = Kp * erreur

        # Calcul des vitesses des moteurs (base + correction)
        spdleft = spd_base + correction
        spdright = spd_base - correction

        # Limitation des vitesses entre 0 et 255
        spdleft = max(-255, min(255, spdleft))
        spdright = max(-255, min(255, spdright))

        # Envoi des commandes aux moteurs
        ard.send_arduino_cmd_motor(spdleft, spdright)

        # Affichage de l'état actuel
        print("Cap actuel: {:.2f}°, Erreur: {:.2f}°, Vitesse gauche: {}, Vitesse droite: {}".format(cap_actuel, erreur, spdleft, spdright))

        # Pause de 0.1 seconde avant la prochaine lecture
        sleep(0.1)

    ard.send_arduino_cmd_motor(0, 0)
    print("Moteurs arrêtés.")

def conversion_spherique_cartesien(point, long_m=3.0144444, lat_m=48.1991667, rho=6371):
    """
    Convertit les coordonnées GPS(latitude, longitude) en coordonnées cartésiennes locales (sur le lac t'as capté?)
    """
    long = point[0]
    lat = point[1]
    lx = rho*np.cos(lat)*np.cos(long)
    ly = rho*np.cos(lat)*np.sin(long)
    rho = rho*np.sin(lat)

    x = rho*np.cos(ly)*(lx-long_m)
    y = rho*(ly-lat_m)

    return x, y
