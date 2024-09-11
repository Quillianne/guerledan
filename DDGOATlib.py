# -*- coding: utf-8 -*-
import sys
import numpy as np
import time
from datetime import *
import os
from time import sleep

# Ajout du chemin vers le répertoire contenant les drivers
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
import arduino_driver_v2 as arddrv
import gps_driver_v2 as gpsdrv



# Initialisation des capteurs et moteurs
imu = imudrv.Imu9IO()
ard = arddrv.ArduinoIO()
gps = gpsdrv.GpsIO()
gps.set_filter_speed("0")

A = np.load("A.npy")
b = np.load("b.npy")


GPS_DATA = []

def convert_to_decimal_degrees(ddmmss, direction):
    # Séparer les degrés et les minutes avec des opérations mathématiques
    degrees = int(ddmmss // 100)  # Diviser par 100 pour obtenir les degrés
    minutes = ddmmss % 100  # Le reste correspond aux minutes

    # Conversion des minutes en degrés
    decimal_degrees = degrees + minutes / 60

    # Si la direction est Sud ou Ouest, on rend la valeur négative
    if direction in ['S', 'W']:
        decimal_degrees = -decimal_degrees

    return decimal_degrees

def get_gps(gps=gps):

    gll_ok, gll_data = gps.read_gll_non_blocking()
    if gll_ok:

        print(gll_data)
        latitude = convert_to_decimal_degrees(gll_data[0], gll_data[1])
        longitude = convert_to_decimal_degrees(gll_data[2], gll_data[3])
        return latitude, longitude

def suivi_gps(point_gps, log=True, Kp = 2):
    obj = np.array(conversion_spherique_cartesien(point_gps))
    distance = 100


    while distance > 5:

        coord_boat = get_gps()
        GPS_DATA.append(coord_boat)
        if coord_boat != None:
            boat = np.array(conversion_spherique_cartesien(coord_boat))

            vecteur = boat-obj
            cap = get_cap()*180/np.pi
            cap_a_suivre = -np.arctan2(vecteur[1],vecteur[0])*180/np.pi
            distance = np.linalg.norm(vecteur)
            # Calcul de l'erreur de cap
            erreur = cap_a_suivre - cap

            # Ajustement de l'erreur pour la circularité (entre -180 et 180 degrés)
            if erreur > 180:
                erreur -= 360
            elif erreur < -180:
                erreur += 360

            print("cap actuel: {:.2f}° | cap à suivre: {:.2f}° | erreur: {:.2f}° | distance: {:.2f}m".format(cap,cap_a_suivre,erreur,distance))
            

            # Correction proportionnelle
            correction = Kp * erreur
            #spd_base = 50+distance
            spd_base = 100


            # Calcul des vitesses des moteurs (base + correction)
            spdleft = spd_base + correction
            spdright = spd_base - correction

            # Limitation des vitesses entre 0 et 255
            spdleft = max(-255, min(255, spdleft))
            spdright = max(-255, min(255, spdright))

            # Envoi des commandes aux moteurs
            ard.send_arduino_cmd_motor(spdleft, spdright)

        time.sleep(0.1)
    
    np.save("gps_data.npy",GPS_DATA)
    ard.send_arduino_cmd_motor(0, 0)

        







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

    ard.send_arduino_cmd_motor(0, 0)

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

def deg_to_rad(deg):
    """Convertit les degrés en radians."""
    return deg * np.pi / 180

def conversion_spherique_cartesien(point, lat_m=48.1991667, long_m=-3.0144444, rho=6371000):
    """
    Convertit les coordonnées GPS (latitude, longitude) en coordonnées cartésiennes locales
    par rapport à un point M défini par lat_m et long_m, en ne retournant que x et y.
    """
    # Convertir les latitudes et longitudes en radians
    lat_m_rad = deg_to_rad(lat_m)
    long_m_rad = deg_to_rad(long_m)
    lat_rad = deg_to_rad(point[0])
    long_rad = deg_to_rad(point[1])

    # Conversion des coordonnées du point M (centre) en cartésiennes 2D (x_m, y_m)
    x_m = rho * np.cos(lat_m_rad) * np.cos(long_m_rad)
    y_m = rho * np.cos(lat_m_rad) * np.sin(long_m_rad)

    # Conversion des coordonnées du point P en cartésiennes 2D (x_p, y_p)
    x_p = rho * np.cos(lat_rad) * np.cos(long_rad)
    y_p = rho * np.cos(lat_rad) * np.sin(long_rad)

    # Calcul des coordonnées relatives par rapport au point M
    x = x_p - x_m
    y = y_p - y_m

    return x, y


def lissajou(t):  #fonction qui retourne le point a rejoindre à l'instant t (cartesien)
    """
    Porte bien son nom
    """
    t0 = 
    a0, a1 = conversion_spherique_cartesien([48.1996457, -3.0152944])
    delta = (40/15)*5

    x = 20*np.sin(t-t0 + delta) + a0
    y = 40*np.sin(2*(t-t0 + delta)) + a1

    return x,y

def lissajou_point(t):  #fonction qui retourne la dérivé du point a rejoindre à l'instant t (cartesien)
    """
    fonction qui retourne la dérivée de lissajou
    """
    t0 = 
    delta = (40/15)*5

    x_point = 20*np.sin(t-t0 + delta)
    y_point = 40*np.sin(2*(t-t0+delta))

    return x_point, y_point



def get_point_boat():
    """
    fonction qui retourne les coordonnees cartesiennes du bateau
    """
    # coordonnées gps (degrés)
    point_gps = get_gps()
    x, y = conversion_spherique_cartesien(point_gps, lat_m=48.1996457, long_m=-3.0152944)

    return x, y

def vecteur_d(position, objectif, vitesse_objectif,ordre_de_grandeur=5): #fonction avec la tan_hyperbolique,etc...

    return x,y

def suivi_trajectoire(fonction, fonction_derive): #fonction qui suit la trajectoire

    #suivi cap: cap_consigne, spd_base (vitesse desirée), duree = 0.1 secondes



# Get the current time in UTC
current_time_utc = datetime.now(timezone.utc)

# Print or use the time
print(current_time_utc)
