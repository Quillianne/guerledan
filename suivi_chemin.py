from DDGOATlib import declenchement, suivi_gps, suivi_chemin_temps
import time


declenchement()
suivi_chemin_temps()
time.sleep(10)
suivi_gps((48.19918833333333, -3.014728333333333))

