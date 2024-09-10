import numpy as np
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv

# http://ensta-bretagne.fr/jaulin/speech_calibration.pdf
def degToRad(deg):
    return deg * np.pi / 180



beta = 46 * 10**(-6)
inclination = 64

imu = imudrv.Imu9IO()

def moyenne_mesures(imu, duree=5):
    """
    Fonction pour capturer les données magnétiques pendant une durée (en secondes) 
    et renvoyer la moyenne des mesures sur cette période.
    """
    start_time = time.time()
    mesures = []

    # Capturer les données pendant 'duree' secondes
    while time.time() - start_time < duree:
        mesures.append(imu.read_mag_raw())

    # Calculer la moyenne des mesures
    moyenne = np.mean(mesures, axis=0)
    return np.array(moyenne)

def calibrateMag(imu):
    """
    Calibrer le magnétomètre avec moyennage des mesures sur 5 secondes pour chaque direction.
    """
    input("Positionner le capteur vers le nord, puis appuyez sur Entrée")
    xn = moyenne_mesures(imu)
    print(xn)

    input("Positionner le capteur vers le sud, puis appuyez sur Entrée")
    xs = moyenne_mesures(imu)
    print(xs)

    input("Positionner le capteur vers l'ouest, puis appuyez sur Entrée")
    xw = moyenne_mesures(imu)
    print(xw)

    input("Positionner le capteur vers le haut, puis appuyez sur Entrée")
    xu = moyenne_mesures(imu)
    print(xu)
    
    # Calcul du biais
    b = -0.5 * (xn + xs)
    
    # Création de la matrice X avec les mesures ajustées pour le biais
    X = np.vstack((xn + b, xw + b, xu + b)).T
    print("Dimensions de X:", X.shape)

    # Calcul des vecteurs théoriques basés sur l'inclinaison magnétique
    yn = np.array([[beta * np.cos(degToRad(inclination))], [0],
                   [-beta * np.sin(degToRad(inclination))]])

    yw = np.array([[0], [-beta * np.cos(degToRad(inclination))],
                   [-beta * np.sin(degToRad(inclination))]])

    yup = np.array([[-beta * np.sin(degToRad(inclination))], [0],
                    [beta * np.cos(degToRad(inclination))]])

    # Création de la matrice Y
    Y = np.hstack((yn, yw, yup))
    print("Dimensions de Y:", Y.shape)

    # Calcul de la matrice de calibration A
    A = X @ np.linalg.inv(Y)
    
    # Sauvegarde des matrices A et b
    np.save('A.npy', A)
    np.save('b.npy', b)

    return A, b


if __name__ == '__main__':
    A, b = calibrateMag(imu)
    print("Matrice de calibration (A):\n", A)
    print("Vecteur de biais (b):\n", b)
