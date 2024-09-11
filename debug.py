import numpy as np
import time
from datetime import datetime

point_gps = [4811.9251, "N", 300.8405, "W"]



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


def get_cap():
    return 0

def get_gps():
    gll_ok, gll_data = True, point_gps
    if gll_ok:
        # Conversion des données GPS en degrés décimaux
        latitude = convert_to_decimal_degrees(gll_data[0], gll_data[1])
        longitude = convert_to_decimal_degrees(gll_data[2], gll_data[3])
        return latitude, longitude

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


def suivi_gps(point_gps, log=True, Kp = 2):
    obj = np.array(conversion_spherique_cartesien(point_gps))
    distance = 100


    while distance > 5:

        coord_boat = get_gps()
        if coord_boat != None:
            boat = np.array(conversion_spherique_cartesien(coord_boat))
            vecteur = obj-boat
            cap = get_cap()*180/np.pi

            cap_a_suivre = np.arctan2(vecteur[1],vecteur[0])*180/np.pi
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
            #ard.send_arduino_cmd_motor(spdleft, spdright)

        time.sleep(0.1)


def lissajou(t, t0 = 1726048800):  #fonction qui retourne le point a rejoindre à l'instant t (cartesien)
    """
    Porte bien son nom, prends en argument un float
    """

    #a0, a1 = conversion_spherique_cartesien([48.1996457, -3.0152944])

    test = point_gps
    latitude = convert_to_decimal_degrees(test[0], test[1])
    longitude = convert_to_decimal_degrees(test[2], test[3])
    a0,a1 = conversion_spherique_cartesien((latitude,longitude))

    delta = (40/15)*5

    x = 10.4*np.sin(2*np.pi*(t-t0 + delta)/40) + a0
    y = 10.4*np.sin(2*(2*np.pi*(t-t0 + delta)/40)) + a1

    return x,y

def lissajou_point(t, t0 = 1726048800):  #fonction qui retourne la dérivé du point a rejoindre à l'instant t (cartesien)
    """
    fonction qui retourne la dérivée de lissajou
    """
    delta = (40/15)*5

    x_point = 2*np.pi*10.4*np.cos(2*np.pi*(t-t0 + delta)/40)/40
    y_point = 2*np.pi*2*10.4*np.cos(2*(2*np.pi*(t-t0 + delta)/40))/40

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

def vecteur_d(position:np.array, objectif:np.array, vitesse_objectif:np.array, ordre_de_grandeur=5, Kp=10)->np.array: 
    """
    fonction avec la tan_hyperbolique,etc...
    """
    # erreur : vecteur entre les 2 points
    e = objectif - position
    #print("e: ", e)
    #print("vitesse obj: ", vitesse_objectif)
    e_norm = np.linalg.norm(e)
    #print("distance :", e_norm)
    d = (Kp * e/e_norm * np.tanh(e_norm/ordre_de_grandeur) + vitesse_objectif/10)
    #print("d: ",d)
    return d



def suivi_trajectoire(fonction, fonction_derive): #fonction qui suit la trajectoire
    t_start = time.time()
    data_lissajou = []
    while True:

        coord_boat = get_point_boat()
        data_lissajou.append(coord_boat)
        obj = np.array(fonction(datetime.now().timestamp()))
        vitesse_obj = np.array(fonction_derive(datetime.now().timestamp()))
        if coord_boat != None:

            vecteur = vecteur_d(coord_boat, obj, vitesse_obj)
            cap = np.arctan2(vecteur[1],vecteur[0])*180/np.pi
            #print(cap)
            vitesse = min(25*np.linalg.norm(vecteur),255)
            print(vitesse)

        if (time.time() - t_start) > 300:
            break

        time.sleep(0.1)



print(get_gps())
print(conversion_spherique_cartesien(get_gps()))

print(conversion_spherique_cartesien((48.1996457, -3.0152944)))

#suivi_gps((48.1996457, -3.0152944))

print(suivi_trajectoire(lissajou,lissajou_point))
