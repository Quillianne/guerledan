## -*- coding: utf-8 -*-
import sys
import numpy as np
import time
from datetime import datetime
import os

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

def suivi_gps(point_gps, log=True, Kp=2, vitesse_max=200, distance_seuil=5):
    """
    Fonction pour suivre un point GPS cible avec régulation en cap et en vitesse.
    La vitesse est ajustée en fonction de la distance avec la tangente hyperbolique (tanh).
    """

    # Conversion du point GPS cible en coordonnées cartésiennes
    obj = np.array(conversion_spherique_cartesien(point_gps))
    distance = 100  # Valeur initiale de distance pour entrer dans la boucle

    # Liste pour enregistrer les données GPS
    GPS_DATA = []

    while distance > distance_seuil:
        # Obtenir les coordonnées actuelles du bateau en GPS
        coord_boat = get_gps()

        # Ajouter la position GPS du bateau à la liste
        if coord_boat:
            GPS_DATA.append(coord_boat)

            # Conversion des coordonnées du bateau en cartésiennes
            boat = np.array(conversion_spherique_cartesien(coord_boat))

            # Calculer le vecteur vers le point cible
            vecteur = obj - boat

            # Calcul de la distance au point cible
            distance = np.linalg.norm(vecteur)

            # Obtenir le cap actuel du bateau
            cap = get_cap() * 180 / np.pi

            # Calcul du cap à suivre (angle vers le point cible)
            cap_a_suivre = np.arctan2(vecteur[1], vecteur[0]) * 180 / np.pi

            # Calcul de l'erreur de cap
            erreur = cap_a_suivre - cap

            # Ajustement de l'erreur pour la circularité (entre -180 et 180 degrés)
            if erreur > 180:
                erreur -= 360
            elif erreur < -180:
                erreur += 360

            print("Cap actuel: {:.2f}° | Cap à suivre: {:.2f}° | Erreur: {:.2f}° | Distance: {:.2f}m".format(cap,cap_a_suivre,erreur,distance))

            # Correction proportionnelle pour le cap
            correction = Kp * erreur

            # Ajuster la vitesse en fonction de la distance avec la tangente hyperbolique
            vitesse = np.tanh(distance / distance_seuil) * vitesse_max

            # Calcul des vitesses des moteurs (base + correction cap)
            spdleft = vitesse + correction
            spdright = vitesse - correction

            # Limiter les vitesses entre -255 et 255
            spdleft = max(-255, min(255, spdleft))
            spdright = max(-255, min(255, spdright))

            # Envoyer les commandes aux moteurs
            ard.send_arduino_cmd_motor(spdleft, spdright)

        # Pause avant la prochaine itération
        time.sleep(0.1)

    # Sauvegarder les données GPS à la fin du suivi
    np.save("gps_data.npy", GPS_DATA)

    # Arrêter les moteurs
    ard.send_arduino_cmd_motor(0, 0)
    print("Arrêt des moteurs.")

def get_gps(gps=gps):

    gll_ok, gll_data = gps.read_gll_non_blocking()
    if gll_ok:

        print(gll_data)
        latitude = convert_to_decimal_degrees(gll_data[0], gll_data[1])
        longitude = convert_to_decimal_degrees(gll_data[2], gll_data[3])
        return latitude, longitude

# def suivi_gps(point_gps, log=True, Kp = 2):
#     obj = np.array(conversion_spherique_cartesien(point_gps))
#     distance = 100


#     while distance > 5:

#         coord_boat = get_gps()
#         GPS_DATA.append(coord_boat)
#         if coord_boat != None:
#             boat = np.array(conversion_spherique_cartesien(coord_boat))

#             vecteur = obj-boat
#             cap = get_cap()*180/np.pi
#             cap_a_suivre = np.arctan2(vecteur[1],vecteur[0])*180/np.pi
            
#             distance = np.linalg.norm(vecteur)
#             # Calcul de l'erreur de cap
#             erreur = cap_a_suivre - cap

#             # Ajustement de l'erreur pour la circularité (entre -180 et 180 degrés)
#             if erreur > 180:
#                 erreur -= 360
#             elif erreur < -180:
#                 erreur += 360

#             print("cap actuel: {:.2f}° | cap à suivre: {:.2f}° | erreur: {:.2f}° | distance: {:.2f}m".format(cap,cap_a_suivre,erreur,distance))
            

#             # Correction proportionnelle
#             correction = Kp * erreur
#             #spd_base = 50+distance
#             spd_base = 100


#             # Calcul des vitesses des moteurs (base + correction)
#             spdleft = spd_base + correction
#             spdright = spd_base - correction

#             # Limitation des vitesses entre 0 et 255
#             spdleft = max(-255, min(255, spdleft))
#             spdright = max(-255, min(255, spdright))

#             # Envoi des commandes aux moteurs
#             ard.send_arduino_cmd_motor(spdleft, spdright)

#         time.sleep(0.1)
    
#     np.save("gps_data.npy",GPS_DATA)
#     ard.send_arduino_cmd_motor(0, 0)

        

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
        time.sleep(0.1)

    if duree > 10:
        ard.send_arduino_cmd_motor(0, 0)
        print("Moteurs arrêtés.")

def deg_to_rad(deg):
    """Convertit les degrés en radians."""
    return deg * np.pi / 180

def conversion_spherique_cartesien(point, lat_m=48.1996872, long_m=-3.0153766, rho=6371000):
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

    return -x, y


def lissajou(t, t0 = 1726048800):  #fonction qui retourne le point a rejoindre à l'instant t (cartesien)
    """
    Porte bien son nom, prends en argument un float
    """
    a0, a1 = conversion_spherique_cartesien([48.1996457, -3.0152944])


    delta = (40/15)*5

    x = 10.4*np.sin(2*np.pi*(t-t0 + delta)/100) + a0
    y = 10.4*np.sin(2*(2*np.pi*(t-t0 + delta)/100)) + a1

    return x,y

def lissajou_point(t, t0 = 1726048800):  #fonction qui retourne la dérivé du point a rejoindre à l'instant t (cartesien)
    """
    fonction qui retourne la dérivée de lissajou
    """
    delta = (40/15)*5

    x_point = 2*np.pi*10.4*np.cos(2*np.pi*(t-t0 + delta)/100)/100
    y_point = 2*np.pi*2*10.4*np.cos(2*(2*np.pi*(t-t0 + delta)/100))/100

    return x_point, y_point



def get_point_boat():
    """
    fonction qui retourne les coordonnees cartesiennes du bateau
    """
    # coordonnées gps (degrés)
    point_gps = get_gps()
    if point_gps != None:
        x, y = conversion_spherique_cartesien(point_gps)

        return x, y

# def vecteur_d(position:np.array, objectif:np.array, vitesse_objectif:np.array, ordre_de_grandeur=5, Kp=10)->np.array: 
#     """
#     fonction avec la tan_hyperbolique,etc...
#     """
#     # erreur : vecteur entre les 2 points
#     e = objectif - position
#     #print("e: ", e)
#     #print("vitesse obj: ", vitesse_objectif)
#     e_norm = np.linalg.norm(e)
#     #print("distance :", e_norm)
#     d = (Kp * e/e_norm * np.tanh(e_norm/ordre_de_grandeur) + vitesse_objectif/10)
#     #print("d: ",d)
#     return d

# def suivi_trajectoire(fonction, fonction_derive): #fonction qui suit la trajectoire
#     t_start = time.time()
#     data_lissajou = []
#     cap_actuel = 0
#     i = 0
#     while True:

#         coord_boat = get_point_boat()
#         data_lissajou.append(coord_boat)
#         obj = np.array(fonction(datetime.now().timestamp()))
#         vitesse_obj = np.array(fonction_derive(datetime.now().timestamp()))
#         if coord_boat != None:

#             vecteur = vecteur_d(coord_boat, obj, vitesse_obj)
#             cap = np.arctan2(vecteur[1],vecteur[0])*180/np.pi
#             vitesse = min(25*np.linalg.norm(vecteur),255)


#             # Conversion du cap en degrés
#             cap_actuel = (cap_actuel + cap)/2
#             # Calcul de l'erreur de cap
#             erreur = cap - cap_actuel

#             # Ajustement de l'erreur pour la circularité (entre -180 et 180 degrés)
#             if erreur > 180:
#                 erreur -= 360
#             elif erreur < -180:
#                 erreur += 360

#             # Correction proportionnelle
#             correction = erreur

#             # Calcul des vitesses des moteurs (base + correction)
#             spdleft = vitesse + correction
#             spdright = vitesse - correction

#             # Limitation des vitesses entre 0 et 255
#             spdleft = max(-255, min(255, spdleft))
#             spdright = max(-255, min(255, spdright))

#             # Envoi des commandes aux moteurs
#             ard.send_arduino_cmd_motor(spdleft, spdright)

#             # Affichage de l'état actuel
#             if i % 5 == 0:
#                 print("Cap actuel: {:.2f}°, Erreur: {:.2f}°,Distance: {:.2f}m, Vitesse gauche: {:.2f}, Vitesse droite: {:.2f}".format(cap_actuel, erreur,np.linalg.norm(obj-coord_boat), spdleft, spdright))
#             i += 1
#             # Pause de 0.1 seconde avant la prochaine lecture
#             time.sleep(0.1)


#         if (time.time() - t_start) > 240:
#             break

#         time.sleep(0.1)

#     ard.send_arduino_cmd_motor(0, 0)
#     np.save("data_lissajou.npy",data_lissajou)
#     print("Moteurs arrêtés.")
    

def suivi_trajectoire(fonction, fonction_derive,duree=300, Kp_cap=2, Kp_vitesse=2, vitesse_max=200, distance_seuil=5):
    """
    Suivi de la trajectoire définie par la fonction lissajou avec régulation en cap et en vitesse.
    La vitesse est régulée en fonction de la distance avec une tangente hyperbolique.
    """
    start_time = time.time()

    data_lissajou = []

    while time.time() - start_time < duree:
        # Récupérer le point cible actuel de la trajectoire de Lissajou
        t = datetime.now().timestamp()
        x_cible, y_cible = fonction(t)
        
        # Récupérer la vitesse cible (dérivée de Lissajou)
        vx_cible, vy_cible = fonction_derive(t)

        # Obtenir la position actuelle du bateau en coordonnées cartésiennes
        point_boat = get_point_boat()
        if point_boat is not None:
            x_bateau, y_bateau = point_boat



            # Calculer le vecteur vers le point cible
            vecteur_cible = np.array([x_cible - x_bateau, y_cible - y_bateau])
            distance = np.linalg.norm(vecteur_cible)  # Distance au point cible

            # Calcul de l'angle de cap à suivre (en degrés)
            cap_a_suivre = np.arctan2(vecteur_cible[1], vecteur_cible[0]) * 180 / np.pi

            # Obtenir le cap actuel du bateau
            cap_actuel = get_cap() * 180 / np.pi

            # Calcul de l'erreur de cap
            erreur_cap = cap_a_suivre - cap_actuel

            # Ajuster l'erreur pour qu'elle soit entre -180 et 180 degrés
            if erreur_cap > 180:
                erreur_cap -= 360
            elif erreur_cap < -180:
                erreur_cap += 360

            # Correction proportionnelle pour le cap
            correction_cap = Kp_cap * erreur_cap
            print("corr cap: ",correction_cap)
            # Calcul de la vitesse désirée en fonction de la distance (tanh pour un ajustement progressif)
            vitesse = np.tanh(distance / distance_seuil) * vitesse_max

    

            # Régulation proportionnelle de la vitesse
            
            print("corr vit: ", vitesse)
            # Calcul des vitesses des moteurs (base + correction cap)
            spdleft = vitesse + correction_cap
            spdright = vitesse - correction_cap

            # Limiter les vitesses des moteurs entre -255 et 255
            spdleft = max(-255, min(255, spdleft))
            spdright = max(-255, min(255, spdright))

            # Envoyer les commandes aux moteurs
            ard.send_arduino_cmd_motor(spdleft, spdright)

            # Affichage de l'état actuel
            print("Cap actuel: {:.2f}°, Cap à suivre: {:.2f}°, Erreur: {:.2f}°, Vitesse: {:.2f}, Distance: {:.2f}m".format(cap_actuel, cap_a_suivre, erreur_cap, vitesse, distance))
            data_lissajou.append(((x_bateau,y_bateau),(x_cible,y_cible),cap_actuel,cap_a_suivre,vitesse,distance))
            # Pause avant la prochaine itération
            time.sleep(0.1)
            np.save("data_lissajou.npy",data_lissajou)

    # Arrêt des moteurs après la durée spécifiée
    ard.send_arduino_cmd_motor(0, 0)
    
    print("Moteurs arrêtés.")











# coordonnées GPS des points importants :
point_M = (48.1996872, -3.0153766)
point_A = (48.1996457, -3.0152944)
point_B = (48.2008333, -3.0163889)
point_C = (48.2019444, -3.0147222)


def cap_chemin(p, m=[48.1996872, -3.0153766], A=[48.1996457, -3.0152944]):

    """"
    Fonction qui retourne le cap en radians pour suivre une ligne définie par (m, A).
    Le cap s'ajuste en fonction de la distance perpendiculaire du point 'p' à cette ligne.

    Args:
        p (list): Point cartesien x,y du bateau.
        m (list): Point GPS (latitude, longitude) de la ligne de départ.
        A (list): Point GPS (latitude, longitude) de la ligne d'arrivée.

    Returns:
        float: Cap à suivre en radians.
    """

    # Conversion des points en coordonnées cartésiennes
    m_car = np.array(conversion_spherique_cartesien(m))
    A_car = np.array(conversion_spherique_cartesien(A))
    p_car = np.array(p)

    # Vecteur directeur de la ligne (m, A)
    vect_mA = (A_car - m_car)
    vect_mA = vect_mA/np.linalg.norm(vect_mA)

    # Cap de la ligne (angle entre la ligne et l'axe x)
    chemin = np.arctan2(vect_mA[1], vect_mA[0]) + np.pi
    print('le chemin est', (chemin*180/np.pi))
    # Calcul de la distance perpendiculaire du point p à la droite définie par (m, A)
    distance = np.cross(vect_mA, p_car - m_car) / np.linalg.norm(vect_mA)
    print('la distance est ', distance)
    # Ajustement du cap en fonction de la distance perpendiculaire
    correction = np.tanh(distance / 5)  # Atténuation avec tanh
    print('la correction est', (correction*180/np.pi))
    # Cap corrigé
    cap_corrige = chemin + correction

    return cap_corrige


def suivi_chemin_temps(point_1=point_M, point_2=point_A, duree=120, Kp_cap=2, vitesse=120):
    """
    Suivi du chemin en ligne droite tracé entre les points 1 et 2 avec régulation en cap et en vitesse.
    point_1 et point_2 doivent être en GPS
    """
    start_time = time.time()
    # boucle qui tourne pendant 'duree'
    while time.time() < start_time + duree:
        
        position_boat = get_point_boat()
        if position_boat is not None:
            # cap à suivre
            cap_objectif = cap_chemin(position_boat, point_1, point_2) * 180/np.pi
            print("LA FONCTION CAP_CHEMIN DE NOE RENVOIE : ", cap_objectif)

            suivi_cap(cap_objectif, 0.1, spd_base=vitesse)




            # # erreur de cap entre les 2
            # erreur = cap_objectif - cap_boat
            # # Ajuster l'erreur pour qu'elle soit entre -180 et 180 degrés
            # if erreur_cap > 180:
            #     erreur_cap -= 360
            # elif erreur_cap < -180:
            #     erreur_cap += 360
            
            # # correction pour contrôler les moteurs
            # correction_cap = Kp_cap * erreur

            # # commande moteurs
            # spdleft = vitesse + correction_cap
            # spdright = vitesse - correction_cap

            # # Limiter les vitesses des moteurs entre -255 et 255
            # spdleft = max(-255, min(255, spdleft))
            # spdright = max(-255, min(255, spdright))

            # # Envoyer les commandes aux moteurs
            # ard.send_arduino_cmd_motor(spdleft, spdright)

            # # Pause avant la prochaine itération
            # time.sleep(0.1)


    # Arrêt des moteurs après la durée spécifiée
    ard.send_arduino_cmd_motor(0, 0)
    
    print("Moteurs arrêtés.")
