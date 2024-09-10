# -*- coding: utf-8 -*-
import sys
import numpy as np
import time
import os
from time import sleep
from .DDGOATlib import declenchement, suivi_cap
# Ajout du chemin vers le répertoire contenant les drivers
sys.path.append(os.path.join(os.path.dirname(__file__), 'drivers-ddboat-v2'))

import imu9_driver_v2 as imudrv
import arduino_driver_v2 as arddrv

# Initialisation des capteurs et moteurs
imu = imudrv.Imu9IO()
ard = arddrv.ArduinoIO()





# Le bloc suivant sera exécuté uniquement si ce fichier est exécuté directement
if __name__ == '__main__':
    
    declenchement()
    # Démarrage du suivi du cap avec une durée de 1 minute
    suivi_cap(cap_consigne=-45, duree=32)
    time.sleep(30)
    suivi_cap(cap_consigne=135, duree=30)
    

