from DDGOATlib import suivi_gps, declenchement
import time

declenchement()
#du ponton vers la bouée
suivi_gps((48.1996457, -3.0152944))
time.sleep(10)
#de la bouée vers le ponton
suivi_gps((48.1992385, -3.0147241))
